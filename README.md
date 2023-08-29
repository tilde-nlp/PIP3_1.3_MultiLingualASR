# PIP3 ...

TODO: description, i.e. LM corpus enrichment method

## Installation

### Python dependencies

Python 3 is recommended.

``` pip install -r requirments.txt ```

### Marian-NMT

Needed to run transliterator model, can be omitted for transcription method.

[https://marian-nmt.github.io/quickstart/](https://marian-nmt.github.io/quickstart/)

``` 
git clone https://github.com/marian-nmt/marian
mkdir marian/build
cd marian/build
cmake ..
make -j4
```

## Input data

- Parallel corpus of source-target language sentences (en-lv)

``` 
data/train.notestdev.en 

maybe he was here trying to get some kind of job .
he may have filled out an application .
```

``` 
data/train.notestdev.lv 

varbūt atbrauca šurp , lai pieteik tos .
varbūt uzrak stījis iesniegumu .
```

- Source-target forward and backward word alignments for the parallel corpus

``` 
data/train.notestdev.en-lv.forward-align 

0-0 3-2 4-3 5-4 4-5 5-6 11-7
1-0 3-1 6-3 7-4
```

``` 
data/train.notestdev.en-lv.backward-align

0-0 2-1 3-2 4-3 9-6 11-7
1-0 6-3 7-4
```

- Source language (en) word frequency list for target word extraction. _NOTE: this is just a proposed way for selecting words of desired frequency, any list of target words can be supplied in theory._
``` 
data/en.not_stemmed.idf

the     0.579
of      0.805
and     0.945
to      1.001
in      1.122
for     1.469
```

- Optionally - list of source language stop words (i.e., overly common words) to filter out
``` 
data/en.not_stemmed.idf

a
able
about
above
abst
accordance
```

## Processing stage description

**NOTE: based on run_transliterate.sh. Some of these steps are omitted in run_transcribe.sh**

### Stage 1: filter alignments

Alignments are filtered such that only sentences that match word-to-word (e.g., not word-to-two-words) are kept. 
Note that this is different from 1:1 alignment.

- Inputs:

    - data/train.notestdev.en-lv.forward-align
    - data/train.notestdev.en-lv.backward-align


- Outputs:
  
    - ``` 
      filtered_alignments
      id|fwd-algn|bwd-algn
      
      1|1-0 3-1 6-3 7-4|1-0 6-3 7-4
      2|0-0 1-2 2-3 3-4 7-8|0-0 1-2 2-3 3-4 4-5 6-6 7-8 8-9
      3|0-0 1-1 2-3 9-4 11-5 12-6 6-7 7-8 13-9|0-0 1-1 6-2 7-3 9-4 11-5 12-6 13-9
      ```
### Stage 2: filter sentences

Filter out sentences from parallel corpus that do not have valid alignments, identified in the previous step.

- Inputs:
    - data/train.notestdev.en
    - data/train.notestdev.lv
    - filtered_alignments

- Outputs:
  
    - ``` 
      aligned_text_raw
      id|fwd-algn|bwd-algn|source-text|target-text
      
      1|1-0 3-1 6-3 7-4|1-0 6-3 7-4|he may have filled out an application .|varbūt uzrak stījis iesniegumu .
      2|0-0 1-2 2-3 3-4|0-0 1-2 2-3 3-4|nobody but you .|neviens , tikai jūs .
      3|1-0 2-3 3-4 4-5|0-0 1-1 2-3 3-4 4-5|I mean before today ?|tas ir , pirms šodienas ?
      ```

### Stage 3: generate POS tags

POS tags are generated for target (lv) sentences. The tags are needed for transliterator input.

- Inputs:

    - aligned_text_raw


- Outputs:
  
    - ``` 
      lv_tags
      given-form|normal-form|tag
      
      varbūt|varbūt|Q-------------------------l- uzrak|uzrak|----------------------------
      Keldai|Kelda|N-fsd---------------------f- gandrīz|gandrīz|R----p---------------g----l-
    

### Stage 4: Add POS tags to aligned sentences

Tags are added to the alignment-sentence file to create the final form of the parallel corpus.

- Inputs:

    - aligned_text_raw
    - lv_tags


- Outputs:
  
    - ``` 
      aligned_tagged_text_raw
      id|fwd-algn|bwd-algn|source-text|target-text|tags
      
      1|0-0 1-2 2-3 3-4|0-0 1-2 2-3 3-4|nobody but you .|neviens , tikai jūs .|p0msn0000000z0000000000000l0 t00000000000000000000000000, q0000000000000000000000000l0 p00pn0200000p0000000000000l0 t00000000000000000000000000.
      ```
  

### Stage 5: Generate list of target words in source language based on frequency

Point of interest target words from source language (en) are extracted using upper and lower frequency bounds for frequency.
Depending on the target domain, bounds can be adjusted to favour more rare or frequent words by passing _--lower_ and _--upper_ to _stem_idf_extract_words.py_ script.
Additionally, stop-words (i.e., too frequent words) are filtered out using a stop-word corpus.

- Inputs:

    - data/en.not_stemmed.idf
    - data/stop-words.en


- Outputs:
  
    - ``` 
      en.lower_12_5_upper_0_0
      
      commission 2.921
      article 2.955
      member 3.19
      european 3.24
      regulation 3.366
      services 3.406
      ```
      
### Stage 6: Extract candidate sentences and source-target word pairs

Sentences containing words of interest are extracted from align-sent-tag file.
Additionally, the identified source-target (en-lv) word pairs are stored alongside the corresponding target POS tag.

- Inputs:

    - en.lower_12_5_upper_0_0
    - aligned_tagged_text_raw


- Outputs:
  
    - ``` 
      candidate_sentences.txt
      target-idx|target-sent|tag source-word target-word
      
      1|varbūt uzrak stījis iesniegumu .|0000000000000000000000000000 filled uzrak
      3|varbūt uzrak stījis iesniegumu .|n0msa000000000000000000000l0 application iesniegumu
      1|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|vs0000300i0000000000000000l0 noticed ievēroja
      4|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|n0msn000000000000000000000l0 smile smaids

      ```
      
    - ``` 
      unique_transl_pairs
      tag source-word target-word
      
      vs0000300i0000000000000000l0 noticed ievēroja
      n0msa000000000000000000000l0 application iesniegumu
      n0msn000000000000000000000l0 smile smaids
      v00000000n0000000000000000l0 guess uzminēt

      ```

### Stage 7: Calculate levenshtein distance for stemmed source-target word pairs

Levenshtein distance for stemmed source-target (en-lv) word pairs is calculated. This needed for further filtering.
Stemming is not strictly necessary and any edit-distance calculator can be used in theory.

- Inputs:

    - unique_pairs

- Outputs:
  
    - ``` 
      pair_scores
      
      0.000
      0.091
      0.400
      0.000
      0.250
      0.500
      ```


### Stage 8: Filter out too similar source-target pairs using Levenshtein scores

Source-target (en-lv) pairs are discarded if Levenshtein distance between them is more than 0.7. 
This is done so that source (en) words that already have a transliterated translation into the target language (lv), 
are not transliterated and used to enrich the LM corpus. Transliterating said words would produce sub-optimal results 
and create words that would not be used in real speech (e.g., there is no point to attempt to transliterate the word "potenciāls").
Similarity threshold can be adjusting by changing _max_lev_ variable in the _run_X.sh_ script.

Additionally, this stage also generates filtered and formatted target word file for transliterator input.

- Inputs:

    - unique_pairs
    - pair_scores

- Outputs:
  
    - ``` 
      unique_pairs_filtered
      tag source-word target-word
      
      vs0000300i0000000000000000l0 noticed ievēroja
      n0msa000000000000000000000l0 application iesniegumu
      n0msn000000000000000000000l0 aloud lamuvārds
      gsmsn00n000a00000000000000l0 maintain izzudis
      ```
    - ``` 
      transl.en
      tag source-word
      
      vs0000300i0000000000000000l0 n o t i c e d
      n0msa000000000000000000000l0 a p p l i c a t i o n
      n0msn000000000000000000000l0 a l o u d
      gsmsn00n000a00000000000000l0 m a i n t a i n
      ```
### Stage 9: Generate transliterations/transcriptions

Source (en) words from the filtered pairs are transliterated using transliterator or transcriber.
Resulting transliterations are added to the filtered source-target (en-lv) word pair file. 
In the adding step, transliterated output is lowercased by default to correct for any erroneous proposed capitalisation by the model.
This behaviour can be changed by passing _--keep_uppercase_ to the _join_translit_pairs.py_ script.
- Inputs:

    - transl.en

- Outputs:
  
    - ``` 
      transl.lv
      
      n o t i c ē j a
      v i s p e l a c i o n ā l ā k ā s
      v i s A l u d ā k ā s
      m a i n t ā n i s k a i s
      ```

    - ``` 
      unique_pairs_filtered_translated
      tag source-word target-word|transliteration
      
      vs0000300i0000000000000000l0 noticed ievēroja|noticēja
      n0msa000000000000000000000l0 application iesniegumu|vispelacionālākās
      n0msn000000000000000000000l0 aloud lamuvārds|visaludākās
      gsmsn00n000a00000000000000l0 maintain izzudis|maintāniskais
      ```

### Stage 10: Calculate levenshtein distance for stemmed transliteration pairs

Levenshtein distance for source-transliteration pairs (e.g., noticed-noticēja) is calculated. This needed for further filtering.
Once again, stemming is not strictly necessary and any edit-distance calculator can be used in theory.

- Inputs:

    - unique_pairs_filtered_translated

- Outputs:
  
    - ``` 
      trans.lv.scores
      
      0.714
      0.267
      0.200
      0.750
      0.167
      0.833
      ```

### Stage 11: Filter sub-optimal transliterations using Levenshtein scores

Generated transliterations that are too different from the input word are discarded.
This filters out poor quality transliterations. 
Similarity threshold can be adjusting by changing _min_lev_ variable in the _run_X.sh_ script.

- Inputs:

    - unique_pairs_filtered_translated
    - trans.lv.scores

- Outputs:
  
    - ``` 
      unique_transl_filtered_translated_clean
      tag source-word target-word|transliteration
      
      vs0000300i0000000000000000l0 noticed ievēroja|noticēja
      gsmsn00n000a00000000000000l0 maintain izzudis|maintāniskais
      ```


### Stage 12: Substitute transliterations into candidate sentences

Final list of filtered transliteration pairs is used to substitute target words in the candidate sentences to form an enriched text corpus.

- Inputs:

    - unique_pairs_filtered_translated_clean
    - candidate_sentences.txt

Since there can often be more than one possible unique substitution per candidate sentence, there substitution methods are provided.
These can be selected by passing the appropriate argument to the _finalise_candidates.py_ script: 

- no argument (i.e., default mode)
  - One substitution is allowed per sentence.
    - ```
        
      1|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|vs0000300i0000000000000000l0 noticed ievēroja
      4|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|n0msn000000000000000000000l0 smile smaids
      8|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|gsmsn00n000a00000000000000l0 maintain izzudis
      
      |      
      |
      V
    
      Kelda **noticēja** , ka smaids viņa acīs nav izzudis .
      Kelda ievēroja , ka **smails** viņa acīs nav izzudis .
      Kelda ievēroja , ka smaids viņa acīs nav **maintāniskais*** .
        ```
  
- _--sample_pool_
  - Multiple substitutions are allowed per sentence. 
    For each sentence possible substitutions are sampled from the available pool with decreasing probability.
    Once a word has been sampled it is removed from the pool. This means that each unique substitution can only occur once.
    - ```
        
      1|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|vs0000300i0000000000000000l0 noticed ievēroja
      4|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|n0msn000000000000000000000l0 smile smaids
      8|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|gsmsn00n000a00000000000000l0 maintain izzudis
      
      |      
      |
      V
    
      Kelda **noticēja** , ka smaids viņa acīs nav izzudis .
      Kelda ievēroja , ka **smails** viņa acīs nav **maintāniskais*** .
        ```

- _--sample_all_
  - Multiple substitutions are allowed per sentence. 
    For each sentence possible substitutions are sampled from the available pool with decreasing probability.
    Once a word has been sampled it is **NOT** removed from the pool. 
    Sampling and substituting continues until every word has been sampled at least once.
    - ```
        
      1|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|vs0000300i0000000000000000l0 noticed ievēroja
      4|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|n0msn000000000000000000000l0 smile smaids
      8|Kelda ievēroja , ka smaids viņa acīs nav izzudis .|gsmsn00n000a00000000000000l0 maintain izzudis
      
      |      
      |
      V
    
      Kelda **noticēja** , ka smaids viņa acīs nav izzudis .
      Kelda **noticēja** , ka smaids viņa acīs nav **maintāniskais*** .
      Kelda ievēroja , ka smaids viņa acīs nav **maintāniskais*** .
      Kelda **noticēja** , ka **smails** viņa acīs nav **maintāniskais*** .
        ```

- Outputs:
  
    - ``` 
      final.txt
      
      Kelda noticēja , ka smaids viņa acīs nav izzudis .
      Kelda noticēja , ka smaids viņa acīs nav maintāniskais .
      Kelda ievēroja , ka smaids viņa acīs nav maintāniskais .
      Kelda noticēja , ka **smails** viņa acīs nav maintāniskais .
      ```

    - Also write a control corpus, with matching sentence amount, but without substitutions.
      This can be used to train a baseline LM model. 
      It is, however, recommended to remove duplicates before any training.
      ``` 
      final_no_replace.txt
      
      Kelda ievēroja , ka smaids viņa acīs nav izzudis .
      Kelda ievēroja , ka smaids viņa acīs nav izzudis .
      Kelda ievēroja , ka smaids viņa acīs nav izzudis .
      Kelda ievēroja , ka smaids viņa acīs nav izzudis .
      ```






  







