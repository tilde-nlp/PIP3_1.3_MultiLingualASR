
def main(args):

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

                    # e.g. 2|0-0|0-0|summary|kopsavilkums|n0msn000000000000000000000l0
                    line = line + "|" + " ".join(tag_str)
                    out_f.write(line + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--alignment_text', type=str, required=True, help='path to alignments and text file')
    parser.add_argument('--tags', type=str, required=True, help='path to POS tags file')
    parser.add_argument('--out', type=str, required=True, help='path to out folder')

    args = parser.parse_args()

    # run main
    main(args)