from collections import defaultdict
from tqdm import tqdm


def main(args):
    # hash map of target words
    target_words = defaultdict(int)
    # set of all words
    all_words = set()
    # parse target words
    with open(args.target, 'r', encoding='utf-8') as in_f:
        lines = in_f.readlines()
        for line in lines:
            line = line.strip()
            line = line.split()
            word = line[0]
            all_words.add(word)
            target_words[word] += 1

    # keep track of used words
    used_words = set()

    # keep track of unique word pairs
    uniq_pairs = set()

    # stat counts
    written_sent = 0
    total_sent = 0
    discarded = 0
    uniq_sent = 0

    with open(args.parallel, 'r', encoding='utf-8') as in_f:

        # output sentences with corresponding matches source-target pair
        with open(args.out + "/candidate_sentences.txt", 'w', encoding='utf-8', newline='\n') as out_f:

            # parse parallel data
            # e.g. # e.g. 2|0-0|0-0|summary|kopsavilkums|n0msn000000000000000000000l0
            lines = in_f.readlines()
            print("Matching target words with sentences...")
            for line in tqdm(lines):
                total_sent += 1
                line = line.strip()
                line = line.split("|")
                # check if forward alignment exists
                fwd_align = line[1].split(" ")
                if fwd_align == ['']:
                    discarded += 1
                    continue

                source_text = line[3].split(" ")
                target_text = line[4].split(" ")
                target_tags = line[5].split(" ")

                # keep track of unique sentences
                used = False

                # loop trough alignments
                for algn in fwd_align:

                    idx = algn.split("-")
                    source_idx = int(idx[0])  # en
                    target_idx = int(idx[1])  # lv

                    # if source word matches desired target word, add sentence to the data
                    # repeat for each word of the sentence
                    if target_words[source_text[source_idx]] > 0:
                        # keep track of used words
                        used_words.add(source_text[source_idx])

                        # e.g. 0|konta izveides norādījumi|n0msg000000000000000000000l0 account konta
                        out_f.write(
                            str(target_idx) + "|" +
                            " ".join(target_text) + "|" +
                            target_tags[target_idx] + " " +
                            source_text[source_idx] + " " +
                            target_text[target_idx] + "\n")

                        # keep track of unique source-target pairs
                        uniq_pairs.add(target_tags[target_idx] + " "
                                       + source_text[source_idx] + " "
                                       + target_text[target_idx])

                        # count total sentences
                        written_sent += 1
                        used = True

                # count unique sentences
                if used:
                    uniq_sent += 1

    # output just source target pairs with POS tag for transliterator
    with open(args.out + "/unique_transl_pairs.txt", 'w', encoding='utf-8', newline='\n') as out_f:
        for pair in uniq_pairs:
            out_f.write(pair + "\n")

    print("Discarded %s sentences with missing forward alignment." % discarded)
    print("Used %s/%s [%s %s] words." % (
        len(used_words), len(all_words), round(100 * len(used_words) / len(all_words), 2), "%"))
    print("Used %s/%s [%s %s] sentences." % (
        uniq_sent, total_sent, round(100 * uniq_sent / total_sent, 2), "%"))
    print("Total %s candidate sentences." % written_sent)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--target', type=str, required=True, help='path to target words of interest')
    parser.add_argument('--parallel', type=str, required=True, help='path to parallel corpus with tags and alignments')
    parser.add_argument('--out', type=str, required=True, help='path to out dir')

    args = parser.parse_args()

    # run main
    main(args)
