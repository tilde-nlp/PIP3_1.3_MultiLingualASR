#!/usr/bin/env bash

# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail

# --- tools --- #
# pos tagger .sh
pos_tagger=tools/run-lv-factorizer.sh
# levenshtein distance calculator
lev_exe=tools/ScoreCognateOverlapForStemmedWords.exe
# transliterator decoder
decoder=tools/marian-decoder
# transliterator ckpt
ckpt=tools/model.npz.best-translation.npz.decoder.batch.yml

# outdir
out_dir=debug
mkdir -p $out_dir

# parallel data
source_parallel=data/train.notestdev.en       # corresponds to the first index in the alignments (source)
target_parallel=data/train.notestdev.lv       # corresponds to the second index in the alignments (target)
fwd=data/train.notestdev.en-lv.forward-align  # source-target forward alignment
bwd=data/train.notestdev.en-lv.backward-align # source-target backward alignment

# source language identifier
s_lang=en
# target language identifier
t_lang=lv

# idf data
idf=data/en.not_stemmed.idf
stop_words=data/stop-words.en # leave empty if not needed

# lower and upper bounds for IDF filtering
lower=12.5 # 7
upper=0.0
lower_str=${lower/./_}
upper_str=${upper/./_}

# minimum required word similarity as levenshtein distance
min_lev=0.5 # set to 0 to disable
# maximum allowed word similarity as levenshtein distance
max_lev=0.7 # set to 1 to disable

# stages
stage=1
stop_stage=100

# define logger
log() {
  # This function is from espnet
  # https://github.com/espnet/espnet
  local fname=${BASH_SOURCE[1]##*/}
  echo -e "$(date '+%Y-%m-%d %H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

# ------ Parallel data preparation ------ #

if [ $stage -le 1 ] && [ $stop_stage -ge 1 ]; then
  log "Stage 1: Filter alignments"
  python3 ./extract_alignments.py --forward=$fwd \
    --backward=$bwd \
    --out=$out_dir
fi

if [ $stage -le 2 ] && [ $stop_stage -ge 2 ]; then
  log "Stage 2: Filter parallel sentences"
  python3 ./add_text_to_alignments.py --alignments=${out_dir}/filtered_alignments.txt \
    --source=$source_parallel \
    --target=$target_parallel \
    --out=$out_dir
fi

if [ $stage -le 3 ] && [ $stop_stage -ge 3 ]; then
  log "Stage 3: Generate POS tags for target language"
  cat ${out_dir}/aligned_text_raw.txt | cut -d "|" -f5 | bash $pos_tagger >${out_dir}/${t_lang}_tags.txt
fi

if [ $stage -le 4 ] && [ $stop_stage -ge 4 ]; then
  log "Stage 4: Add tags to the filtered alignment-text file"
  python3 ./add_tags_to_alignments.py --alignment_text=${out_dir}/aligned_text_raw.txt \
    --tags=${out_dir}/${t_lang}_tags.txt \
    --out=$out_dir
fi

# ------ Target word preparation ------ #

if [ $stage -le 5 ] && [ $stop_stage -ge 5 ]; then
  log "Stage 5: Generate list of target words in source language based on frequency"
  python3 ./stem_idf_extract_words.py --idf=$idf \
    --stop_words=$stop_words \
    --lower=$lower \
    --upper=$upper \
    --out=$out_dir \
    --lang=$s_lang
fi

if [ $stage -le 6 ] && [ $stop_stage -ge 6 ]; then
  log "Stage 6: Extract candidate sentences and source-target word pairs from parallel corpus by matching target words"
  python3 ./extract_candidate_word_pairs.py --target=${out_dir}/${s_lang}.lower_${lower_str}_upper_${upper_str} \
    --parallel=${out_dir}/aligned_tagged_text_raw.txt \
    --out=$out_dir
fi

if [ $stage -le 7 ] && [ $stop_stage -ge 7 ]; then
  log "Stage 7: Calculate levenshtein distance for stemmed source-target word pairs"

  cat ${out_dir}/unique_transl_pairs.txt | cut -d " " -f2,3 >${out_dir}/temp_pairs.txt
  sed 's/[[:blank:]]/\t/g' ${out_dir}/temp_pairs.txt >${out_dir}/temp_pairs_2.txt
  rm ${out_dir}/temp_pairs.txt
  mono $lev_exe $s_lang $t_lang <${out_dir}/temp_pairs_2.txt >${out_dir}/pair_scores.txt
  rm ${out_dir}/temp_pairs_2.txt

fi

if [ $stage -le 8 ] && [ $stop_stage -ge 8 ]; then
  log "Stage 8: Discard too similar source-target pairs"
  python3 ./filter_scored_pairs.py --pairs=${out_dir}/unique_transl_pairs.txt \
    --scores=${out_dir}/pair_scores.txt \
    --threshold $max_lev \
    --lang=$s_lang \
    --out $out_dir
fi

if [ $stage -le 9 ] && [ $stop_stage -ge 9 ]; then

  log "Stage 9: Generate transliterations of target word"
  CUDA_VISIBLE_DEVICES=1 $decoder -c $ckpt <${out_dir}/transl.${s_lang} >${out_dir}/transl.${t_lang}

  # add transliterations to candidate sentence file
  python3 ./join_translit_pairs.py --pairs=${out_dir}/unique_transl_pairs_filtered.txt \
    --transl=${out_dir}/transl.${t_lang} \
    --out=$out_dir
fi

if [ $stage -le 10 ] && [ $stop_stage -ge 10 ]; then
  log "Stage 10: Calculate levenshtein distance for transliterated source-target word pairs"

  cat ${out_dir}/unique_transl_pairs_filtered_translated.txt | tr '|' ' ' | cut -d " " -f2,4 | tr ' ' '\t' >${out_dir}/trans.${t_lang}.temp
  mono $lev_exe $s_lang $t_lang <${out_dir}/trans.${t_lang}.temp >${out_dir}/trans.${t_lang}.scores
  rm ${out_dir}/trans.${t_lang}.temp

fi

if [ $stage -le 11 ] && [ $stop_stage -ge 11 ]; then
  log "Stage 11: Discard suboptimal source-target transliterations based on minimum required levenshtein distance"
  python3 ./filter_translit_pairs.py --pairs=${out_dir}/unique_transl_pairs_filtered_translated.txt \
    --scores=${out_dir}/trans.${t_lang}.scores \
    --threshold $min_lev \
    --out $out_dir
fi

if [ $stage -le 12 ] && [ $stop_stage -ge 12 ]; then
  log "Stage 12: Substitute transliterations into candidate sentences"
  python3 ./finalise_candidates.py --pairs=${out_dir}/unique_transl_pairs_filtered_translated_clean.txt \
    --sent=${out_dir}/candidate_sentences.txt \
    --sample_all \
    --out $out_dir
fi
