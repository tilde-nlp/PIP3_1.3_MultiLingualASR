def main(args):
    # source target pairs with POS tags
    # e.g. v00000000n00000y0000000000l0 refusal izvēlēties
    with open(args.pairs, 'r', encoding='utf-8') as in_f:

        # transliterated source language words - this is the output of the transliteration tool
        # e.g. "r e f u s ē s i e t"
        with open(args.transl, 'r', encoding='utf-8') as in_f_2:

            # keep the source target pair with POS tag and add the source word transliteration
            # e.g. v00000000n00000y0000000000l0 refusal izvēlēties|refusēsiet
            with open(args.out + "/unique_transl_pairs_filtered_translated.txt", 'w', encoding='utf-8',
                      newline='\n') as out_f:

                pairs = in_f.readlines()
                transl = in_f_2.readlines()

                # sanity
                assert (len(pairs) == len(transl))

                for pair, transl_word in zip(pairs, transl):

                    pair = pair.strip()
                    transl_word = transl_word.strip()
                    if pair == transl_word == "":
                        continue

                    # construct the transliterated word
                    transl_word = "".join(transl_word.split())

                    # normalise the word to be lowercase
                    if not args.keep_uppercase:
                        transl_word = transl_word.lower()

                    out_f.write(pair + "|" + transl_word + "\n")

    logging.info(
        "Saved source-target pairs with transliterations to: %s" % (
                args.out + "/unique_transl_pairs_filtered_translated.txt"))


if __name__ == "__main__":
    import logging

    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)

    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--pairs', type=str, required=True, help='path to pairs with tags')
    parser.add_argument('--transl', type=str, required=True, help='path to transliterations')
    parser.add_argument('--keep_uppercase', action='store_true', required=False,
                        help='keep uppercase in the transliterations. By default transliterations are normalised to be lowercase')
    parser.add_argument('--out', type=str, required=True, help='path to out dir')

    args = parser.parse_args()

    # run main
    main(args)
