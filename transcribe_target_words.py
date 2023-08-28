from tqdm import tqdm

from tools.en2lv_transcriber import Transcriber


# NOTE: this script relies on certain dummy inputs (e.g. POS tag) in order to match Transliterator data pipeline
# this is done to simplify the entire processing pipeline
def main(args):
    # init transcriber
    trs = Transcriber(args.map)

    # parse input words
    # e.g. n0msn000000000000000000000l0 s m i l e
    with open(args.targets, 'r', encoding='utf-8') as in_f:
        with open(args.out + "/transl." + args.lang, 'w', encoding='utf-8', newline='\n') as out_f:

            lines = in_f.readlines()
            logging.info("Generating transcriptions for %s words" % len(lines))
            for line in tqdm(lines):
                line = line.strip()
                if line == "":
                    continue

                # split off the dummy POS tag
                word = "".join(line.split()[1:])

                # transcribe the word
                tr_word = trs.transcribe(word)

                # white space word characters to match transliterator output
                # e.g. s m i l ē j a
                out_f.write(" ".join([*tr_word]) + "\n")


if __name__ == "__main__":
    import logging

    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)

    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--targets', type=str, required=True, help='path to target words including dummy POS tag')
    parser.add_argument('--map', type=str, required=True, help='path to ipa2lv phoneme map .yaml')
    parser.add_argument('--lang', type=str, required=False, help='language identifier for naming', default='lv')
    parser.add_argument('--out', type=str, required=True, help='path to out folder')

    args = parser.parse_args()

    # run main
    main(args)
