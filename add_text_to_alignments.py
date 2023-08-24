from collections import defaultdict


# source - eng
# target - lv

def main(args):

    # read alignments into dictionary
    alignments = defaultdict(str)
    with open(args.alignments, "r", encoding="utf-8") as in_f:

        lines = in_f.readlines()
        for line in lines:

            line = line.strip()
            if line == "":
                continue

            # e.g. 0|0-0 1-1 2-2|0-0 1-1 2-2
            temp = line.split("|")[0]
            alignments[int(temp)] = line

    with open(args.target, "r", encoding="utf-8") as in_target:
        with open(args.source, "r", encoding="utf-8") as in_source:
            with open(args.out + "/aligned_text_raw.txt", 'w', encoding='utf-8', newline='\n') as out_f:

                target_lines = in_target.readlines()
                source_lines = in_source.readlines()

                # sanity
                assert (len(target_lines) == len(source_lines))

                # extract target and source sentences that have valid alignments
                for n, target in enumerate(target_lines):

                    # clean target string
                    target = target.strip()

                    # clean source string
                    source = source_lines[n]
                    source = source.strip()

                    # skip if no alginments or empty string
                    if target == "" or source == "":
                        continue
                    if alignments[n] == "":
                        continue

                    # e.g. 2|0-0|0-0|summary|kopsavilkums
                    out_f.write(alignments[n] + "|" + source + "|" + target + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--alignments', type=str, required=True, help='path to filtered alignments file')
    parser.add_argument('--source', type=str, required=True, help='path to source language in parallel data')
    parser.add_argument('--target', type=str, required=True, help='path to target language in parallel data')
    parser.add_argument('--out', type=str, required=True, help='path to out folder')

    args = parser.parse_args()

    # run main
    main(args)
