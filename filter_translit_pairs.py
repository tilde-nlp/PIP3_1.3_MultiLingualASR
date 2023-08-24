from collections import defaultdict
from tqdm import tqdm


def main(args):
    # init counter
    count = 0

    # source target pairs with POS tag and added source word transliteration
    # e.g. v00000000n00000y0000000000l0 refusal izvēlēties|refusēsiet
    with open(args.pairs, 'r', encoding='utf-8') as in_f:

        # levenshtein score for each transliterated pair
        with open(args.scores, 'r', encoding='utf-8') as in_f_2:
            # out source target pairs with POS tag and added source word transliteration
            # e.g. v00000000n00000y0000000000l0 refusal izvēlēties|refusēsiet
            with open(args.out + "/unique_transl_pairs_filtered_translated_clean.txt", 'w', encoding='utf-8',
                      newline='\n') as out_f:

                pairs = in_f.readlines()
                scores = in_f_2.readlines()

                # sanity
                assert (len(pairs) == len(scores))

                # check each pair against their score
                for pair, score in zip(pairs, scores):
                    pair = pair.strip()
                    score = score.strip()
                    if pair == score == "":
                        continue

                    # if source and target words are too different, then discard them
                    # this is done to avoid discard poor quality transliterations
                    if float(score) >= args.threshold:
                        out_f.write(pair + "\n")
                        # increment extracted pair counter
                        count += 1

    print("Kept %s/%s [%s %s] transliterated pairs." % (
        count, len(pairs), round(100 * count / len(pairs), 2), "%"))
    print("wrote to:", args.out + "/unique_transl_pairs_filtered_translated_clean.txt")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--pairs', type=str, required=True, help='path to pairs with tags')
    parser.add_argument('--scores', type=str, required=True, help='path to levenshtein scores')
    parser.add_argument('--threshold', type=float, required=False, help='minimum allowed levenshtein distance',
                        default=0.5)
    parser.add_argument('--out', type=str, required=True, help='path to out dir')

    args = parser.parse_args()

    # run main
    main(args)
