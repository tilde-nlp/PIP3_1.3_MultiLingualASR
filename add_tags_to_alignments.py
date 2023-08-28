def main(args):
    # add fake tags
    # this is useful for preserving formatting of intermediate files for transcriber pipeline
    if args.dummy:
        logging.info(
            "--dummy was specified, the input POS tag file will be ignored and fake tags will be added instead.")

        with open(args.alignment_text, 'r', encoding='utf-8') as in_f:
            with open(args.out + "/aligned_tagged_text_raw.txt", 'w', encoding='utf-8', newline='\n') as out_f:

                # read lines
                lines = in_f.readlines()

                # parse lines
                for line in lines:
                    line = line.strip()
                    if line == "":
                        continue

                    # count target words in the input string
                    target_words = line.split("|")
                    target_words = target_words[-1].split()

                    # for each target word, add a dummy POS tag
                    tag_str = []
                    for word in target_words:
                        tag_str.append(28 * "0")

                    # add POS tag to alignment-text entries
                    # e.g. 2|0-0|0-0|summary|kopsavilkums|n0msn000000000000000000000l0
                    line = line + "|" + " ".join(tag_str)
                    out_f.write(line + "\n")

    # add real POS tagger generated tags
    # this is necessary for transliterator input, but is not needed for transcriber
    else:
        with open(args.alignment_text, 'r', encoding='utf-8') as in_f:
            with open(args.tags, 'r', encoding='utf-8') as in_f_2:
                with open(args.out + "/aligned_tagged_text_raw.txt", 'w', encoding='utf-8', newline='\n') as out_f:

                    # read lines
                    lines = in_f.readlines()
                    tags = in_f_2.readlines()

                    # sanity
                    assert (len(lines) == len(tags))

                    # parse lines
                    for line, tag in zip(lines, tags):
                        line = line.strip()
                        tag = tag.strip()
                        if line == "" and tag == "":
                            continue

                        # extract tag
                        tag = tag.split()

                        # sanitize the tag string
                        tag_str = []
                        for pos in tag:
                            pos = pos.split("|")[-1]
                            # lowercase output and replace "-" with 0
                            pos = pos.lower().replace("-", "0")
                            tag_str.append(pos)

                        # add POS tag to alignment-text entries
                        # e.g. 2|0-0|0-0|summary|kopsavilkums|n0msn000000000000000000000l0
                        line = line + "|" + " ".join(tag_str)
                        out_f.write(line + "\n")

    logging.info("Saved alignment-text-tag file to: %s" % (args.out + "/aligned_tagged_text_raw.txt"))


if __name__ == "__main__":
    import logging

    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)

    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--alignment_text', type=str, required=True, help='path to alignments and text file')
    parser.add_argument('--tags', type=str, required=True, help='path to POS tags file')
    parser.add_argument('--dummy', action='store_true', required=False, help='adds dummy tags')
    parser.add_argument('--out', type=str, required=True, help='path to out folder')

    args = parser.parse_args()

    # run main
    main(args)
