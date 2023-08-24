### CORE DATA

#### 1. filter alignments

- /tmp/marcis/speech/en-lv/train.notestdev.en-lv.forward-align
- /tmp/marcis/speech/en-lv/train.notestdev.en-lv.backward-align

alignments are filtered such that only sentences that match word-to-word (e.g. not word-to-two-words) are kept

``` python extract_alignments.py``` > filtered_alignments.txt

#### 2. filter sentences

- /tmp/marcis/speech/en-lv/train.notestdev.en
- /tmp/marcis/speech/en-lv/train.notestdev.lv

corresponding en-lv sentences are then filtered using the identified alignments

```python add_text_to_alignments.py``` > aligned_text_raw.txt

#### 3. generate POS tags

POS tags are generated for lv sentences using
```home/TILDE.LV/daiga.deksne/POSTagger/run-lv-factorizer.sh ``` > lv_tags.txt

tags are added to the alignment-sentence file

``` python add_tags.py ``` > aligned_tagged_text_raw.txt

the resulting corpus is of the form:

``` id|fwd-align|bwd-align|en-text|lv-text|lv-tags ```

### EXPERIMENT DATA

#### 1. Extract english words

point of interest english words are extracted from

- /home/TILDE.LV/marcis.pinnis/NMT/mono-for-id/en.not_stemmed.idf

based on a frequency threshold

``` python stem_idf_extract_words.py ``` > v1/en.no_stop.lower_12_5_upper_0_0

additionally stop words are discarded using

- stop.words.en

#### 2. Extract candidate sentences and en-lv word pairs

Sentences containing english words of interest are extracted from align-sent-tag file.
Additionally, the identified en-lv word pairs are stored alongside the corresponding lv tag.

aligned_tagged_text_raw.txt > ``` python extract_candidate_word_pairs.py ``` > v1/candidate_sentences.txt v1/unique_transl_pairs.txt

#### 3. Filter en-lv word pairs based on Levenhstein distance

en-lv pairs are discarded if levenshtein distance between them is more than 0.7. 
This is done so that english words that already have a transliterated translation into Latvian, are not transliterated again.
Stemming and distance scoring is done using:

```mono /home/TILDE.LV/marcis.pinnis/tools/cognate-similarity/ScoreCognateOverlapForStemmedWords.exe```

``` python filter_scored_pairs.py  ``` > unique_transl_pairs_filtered.txt

#### 4. Generate transliterations
English words from the filtered pairs are transliterated using "v3" or "v3 guess" transliterator:

```/home/TILDE.LV/marcis.pinnis/tools/marian-term/build/marian-decoder -c /tmp/marcis/speech/en-lv-translit-v3/models/model.npz.best-translation.npz.decoder.batch.yml``` > v1/transl.lv
```/home/TILDE.LV/marcis.pinnis/tools/marian-term/build/marian-decoder -c /tmp/marcis/speech/en-lv-translit-v3-guess/models/model.npz.best-translation.npz.decoder.batch.yml``` v1/transl.lv.guess

``` python join_translit_pairs.py  ``` > unique_transl_pairs_filtered_translated.txt



#### 5. Filter transliterations based on Levenshtein distance

Generated transliterations are compared to the original english word and discarded if levenshtein distance between them is less than 0.5.
This filters out bad quality transliterations.

``` python filter_translit_pairs.py  ``` > unique_transl_pairs_filtered_clean.txt

#### 6. Substitute transliterations into candidate sentences

Transliterated words from filtered pairs are used to substitute target lv words and form training sentences.

``` python finalise_candidates.py  ``` > final.txt












  







