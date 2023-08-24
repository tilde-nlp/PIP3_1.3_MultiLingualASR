from collections import defaultdict
from tqdm import tqdm
import random
import sys


# sample words to be replaced from a pool
# after sampling the word is removed from the pool, so that each word occurs at most 1 time
# multiple substitutions can occur within the same training sentence
def sample_from_pool(sentence, idx_list):
    # format indexes to have no repeats
    idx_list = list(set(idx_list))
    # make sure created sentences are unique
    sentences = set()
    # init pool
    current_pool = 1 * idx_list
    # shuffle the pool
    random.shuffle(current_pool)

    # while the pool is not exhausted keep sampling words
    while len(current_pool) > 0:
        # init place holder for updated pool
        remaining = []
        # copy sentence
        # TODO: probably shutil.copy is better
        new_sent = 1 * sentence

        # multiple substitutions can happen per sentence
        for n, keys in enumerate(current_pool):
            idx = keys[0]
            key = keys[1]

            # each consecutive word has smaller chance to get sampled
            prob = 100 / (n + 1)
            rolled_prob = random.randint(1, 100)

            # replace the sampled word
            if prob <= rolled_prob:
                new_sent[idx] = key

            # otherwise add the unsampled word to the updated pool
            else:
                remaining.append(keys)

        # if a substitution was made, store the new sentence
        if new_sent != sentence:
            sentences.add(" ".join(new_sent))

        # update the pool of words
        current_pool = remaining

    return sentences


# sample words to be substituted from a pool
# keep randomly sampling until every word occurs at least 1 time
# multiple substitutions can occur within the same training sentence
def sample_from_all(sentence, idx_list):
    # format indexes to have no repeats
    idx_list = list(set(idx_list))
    # make sure created sentences are unique
    sentences = set()
    # store the seen words
    seen = set()
    # shuffle the pool
    random.shuffle(idx_list)

    # keep sampling until every word occurs at least one time
    while sorted(list(seen)) != sorted(idx_list):
        # copy sentence
        # TODO: probably shutil.copy is better
        new_sent = 1 * sentence

        # multiple substitutions can happen per sentence
        for n, keys in enumerate(idx_list):
            idx = keys[0]
            key = keys[1]

            # each consecutive word has smaller chance to get sampled
            prob = 100 / (n + 1)
            rolled_prob = random.randint(1, 100)

            # replace the sampled word
            if prob <= rolled_prob:
                new_sent[idx] = key

                # update the seen word pool
                seen.add(keys)

        # if a substitution was made, store the new sentence
        if new_sent != sentence:
            sentences.add(" ".join(new_sent))

    return sentences


# one substitution per sentence
def simple_sample(sentence, idx_list):
    # format indexes to have no repeats
    idx_list = list(set(idx_list))
    # make sure created sentences are unique
    sentences = set()

    # substitute one word per sentence until all candidate words are used
    for n, keys in enumerate(idx_list):
        # copy sentence
        # TODO: probably shutil.copy is better
        new_sent = 1 * sentence

        idx = keys[0]
        key = keys[1]

        # replace the sampled word
        new_sent[idx] = key
        sentences.add(" ".join(new_sent))

    return sentences


def main(args):
    if args.sample_pool and args.sample_all:
        sys.exit("please specify one or none of [--sample_pool, --sample_all], but not both.")

    # read in the transliteration pairs
    transl = defaultdict(str)
    # source target pairs with POS tag and added source word transliteration
    # e.g. v00000000n00000y0000000000l0 refusal izvēlēties|refusēsiet
    with open(args.pairs, 'r', encoding='utf-8') as in_f:
        lines = in_f.readlines()
        for line in lines:
            line = line.strip()
            if line == "":
                continue
            line = line.split("|")
            transl[line[0]] = line[1]

    # read in the candidate sentences
    sents = defaultdict(list)
    with open(args.sent, 'r', encoding='utf-8') as in_f:
        lines = in_f.readlines()
        for line in tqdm(lines):
            line = line.strip()
            if line == "":
                continue

            # 0|konta izveides norādījumi|n0msg000000000000000000000l0 account konta
            line = line.split("|")
            idx = int(line[0])
            target_sent = line[1]
            key = line[2]

            # get the transliterated word
            transl_word = transl[key]
            if transl_word == "":
                continue

            # store candidate sentence together with possible substitute words
            sents[target_sent].append((idx, transl_word))

    # init counters
    count = 0
    count_control = 0

    with open(args.out + "/final.txt", 'w', encoding='utf-8', newline='\n') as out_replace:
        with open(args.out + "/final_no_replace.txt", 'w', encoding='utf-8', newline='\n') as out_no_replace:

            for sentence in sents:
                words = sents[sentence]
                sentence = sentence.split()

                # pool sample method
                if args.sample_pool:
                    # pool sample
                    out_sents = sample_from_pool(sentence, words)
                    # write control corpus with unchanged sentences
                    if len(out_sents) > 0:
                        out_no_replace.write(" ".join(sentence) + "\n")
                        # increment control sentence counter
                        count_control += 1
                    # write pool sampled sentences
                    for sent in out_sents:
                        out_replace.write(sent + "\n")
                        # increment sentence counter
                        count += 1

                # 'all' sample method
                elif args.sample_all:
                    # all sample
                    out_sents = sample_from_all(sentence, words)
                    # write control corpus with unchanged sentences
                    if len(out_sents) > 0:
                        out_no_replace.write(" ".join(sentence) + "\n")
                        # increment control sentence counter
                        count_control += 1
                    # write all sampled sentences
                    for sent in out_sents:
                        out_replace.write(sent + "\n")
                        # increment sentence counter
                        count += 1

                # simple sample - one substitution per sentence
                else:
                    # simple sample
                    out_sents = sample_from_pool(sentence, words)
                    # write control corpus with unchanged sentences
                    if len(out_sents) > 0:
                        out_no_replace.write(" ".join(sentence) + "\n")
                        # increment control sentence counter
                        count_control += 1
                    # write simple sampled sentences
                    for sent in out_sents:
                        out_replace.write(sent + "\n")
                        # increment sentence counter
                        count += 1

        print("Generated %s sentences with word substitutions." % count)
        print("Generated %s control sentences." % count_control)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--pairs', type=str, required=True, help='path to filtered pairs with tags')
    parser.add_argument('--sent', type=str, required=True, help='path to candidate sentences')
    parser.add_argument('--out', type=str, required=True, help='path to out dir')
    parser.add_argument('--sample_pool', action='store_true', required=False,
                        help='sample word substitutions until every word is sampled at most once')
    parser.add_argument('--sample_all', action='store_true', required=False,
                        help='sample word substitutions until every word is sampled at least once')

    args = parser.parse_args()

    # run main
    main(args)
