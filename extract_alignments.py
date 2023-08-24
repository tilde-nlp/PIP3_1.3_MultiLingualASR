from tqdm import tqdm


# checks if alignment is "word to word"
# i.e. that no word is mapped to more than one word
# NOTE: this is different from 1:1 mapping
def single_occurance_check(alignment):
    # split alignment into source and target indexes
    alignment = alignment.split()
    source = []
    target = []
    for al in alignment:
        al = al.split("-")
        # sanity check
        assert (len(al) == 2)
        source.append(al[0])
        target.append(al[1])

    # discard if there are any repeated indexes in source
    if len(source) != len(set(source)):
        return False

    # discard if there are any repeated indexes in target
    if len(target) != len(set(target)):
        return False

    return True


def main(args):
    with open(args.forward, 'r', encoding='utf-8') as in_f:
        with open(args.backward, 'r', encoding='utf-8') as in_f_2:
            with open(args.out + "/filtered_alignments.txt", 'w', encoding='utf-8') as out_f:

                f_lines = in_f.readlines()
                b_lines = in_f_2.readlines()
                assert (len(f_lines) == len(b_lines))

                # init total sentence counter
                count = 0
                # init successfully extracted sentence counter
                useful = 0

                # parse alignments
                for n, forward in tqdm(enumerate(f_lines)):
                    forward = forward.strip()
                    backward = b_lines[n].strip()
                    if forward == "" and backward == "":
                        continue

                    # check forward
                    if single_occurance_check(forward):
                        # check backward
                        if single_occurance_check(backward):
                            # e.g. 0|0-0 1-1 2-2|0-0 1-1 2-2
                            out_f.write(str(n) + "|" + forward + "|" + backward + "\n")

                            # increment extracted counter
                            useful += 1

                    # increment total counter
                    count += 1

    logging.info("Extracted [%s/%s] %s %s valid alignments" % (useful, count, round(100 * useful / count, 2), "%"))
    logging.info("Saved extracted alignments to: %s" % (args.out + "/filtered_alignments.txt"))


if __name__ == "__main__":
    import logging

    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)

    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--forward', type=str, required=True, help='path to forward alignments file')
    parser.add_argument('--backward', type=str, required=True, help='path to backward alignments file')
    parser.add_argument('--out', type=str, required=True, help='path to out folder')

    args = parser.parse_args()

    # run main
    main(args)
