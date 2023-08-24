def main(args):
    # init counter
    count = 0

    # source target pairs with POS tag
    # e.g. n0msl000000000000000000000l0 forklift autokrāvējā
    with open(args.pairs, 'r', encoding='utf-8') as in_f:

        # scores for each pair
        # e.g. 0.250
        with open(args.scores, 'r', encoding='utf-8') as in_f_2:

            # output filtered source target pairs with POS tags
            # e.g. n0msl000000000000000000000l0 forklift autokrāvējā
            with open(args.out + "/unique_transl_pairs_filtered.txt", 'w', encoding='utf-8', newline='\n') as out_f:

                # output just the source language words and their corresponding target word POS tag
                # this is the required input for transliteration tool
                # e.g. n0msl000000000000000000000l0 f o r k l i f t
                with open(args.out + "/transl." + args.lang, 'w', encoding='utf-8', newline='\n') as out_f_2:

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

                        # if source and target words are too similar, then discard them
                        # this is done to avoid transliterating already too similar words
                        if float(score) < args.threshold:
                            out_f.write(pair + "\n")

                            clean_pair = pair.split()[:2]
                            out_f_2.write(clean_pair[0] + " " + " ".join([*clean_pair[1]]) + "\n")

                            # count useful pairs
                            count += 1

    logging.info("Kept [%s/%s] %s %s source-target pairs for transliteration." % (
        count, len(pairs), round(100 * count / len(pairs), 2), "%"))
    logging.info(
        "Saved filtered source-target pair file with POS tags to: %s" % (
                args.out + "/unique_transl_pairs_filtered.txt"))
    logging.info(
        "Saved filtered and formatted source word file with POS tags to: %s" % (args.out + "/transl." + args.lang))


if __name__ == "__main__":
    import logging

    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)

    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--pairs', type=str, required=True, help='path to target source pairs with POS tags')
    parser.add_argument('--scores', type=str, required=True, help='path to levenshtein scores')
    parser.add_argument('--threshold', type=float, required=False, help='maximum allowed levenshtein distance',
                        default=0.7)
    parser.add_argument('--lang', type=str, required=False, help='source language identifier for naming', default='en')
    parser.add_argument('--out', type=str, required=True, help='path to out dir')

    args = parser.parse_args()

    # run main
    main(args)
