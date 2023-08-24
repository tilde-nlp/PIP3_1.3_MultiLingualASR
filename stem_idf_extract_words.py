from utils import AlphaFilter


def main(args):
    # read stop words into array
    # TODO: this can be look-up table instead for speed up
    stop_words = []
    if args.stop_words and args.stop_words != "":
        with open(args.stop_words, 'r', encoding='utf-8') as in_f:
            lines = in_f.readlines()
            for line in lines:
                line = line.strip()
                if line == "":
                    continue
                stop_words.append(line)

    # init alphabetical char filter
    alpha = AlphaFilter()

    # parse lower/upper bounds and format output string
    lower_bound = args.lower
    lower_string = str(lower_bound).replace(".", "_")
    upper_bound = args.upper
    upper_string = str(upper_bound).replace(".", "_")

    # init counter
    count = 0

    # parse IDF input
    with open(args.idf, 'r', encoding='utf-8') as in_f:
        with open(args.out + "/" + args.lang + ".lower_" + lower_string + "_upper_" + upper_string, 'w',
                  encoding='utf-8') as out_f:

            lines = in_f.readlines()
            # total available words
            word_num = len(lines)

            for n, line in enumerate(lines):
                line = line.strip()
                if line == "":
                    continue

                # read word and frequency
                line = line.split()
                word = line[0]
                freq = float(line[1])

                # discard word if too frequent
                if freq > lower_bound:
                    continue
                # discard word if in stop words
                if word in stop_words:
                    continue
                # discard if contains non-alpha characters
                if alpha.process(word):
                    continue

                # write extracted words and the corresponding frequencies
                out_f.write(word + " " + str(freq) + "\n")

                # increment word counter
                count += 1

    print("Extracted", count, "/", word_num, "[", round(100 * count / word_num, 2), "%", "] usable words")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--idf', type=str, required=True, help='path to idf file')
    parser.add_argument('--stop_words', type=str, required=False, help='path to stop words file for filtering')
    parser.add_argument('--lower', type=float, required=False, help='frequency lowerbound', default=12.5)
    parser.add_argument('--upper', type=float, required=False, help=' frequency upperbound', default=0.0)
    parser.add_argument('--out', type=str, required=True, help='path to out folder')
    parser.add_argument('--lang', type=str, required=False, help='language identifier for naming', default='en')

    args = parser.parse_args()

    # run main
    main(args)
