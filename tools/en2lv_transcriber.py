import sys
import yaml
import eng_to_ipa as ipa


class Transcriber:
    def __init__(self, path_to_map_yaml):

        # load mappings
        mapper = yaml.safe_load(open(path_to_map_yaml, 'r', encoding='utf-8'))
        # get map names
        char_maps = list(mapper.keys())
        # FIXME: hardcoded
        assert (len(char_maps) == 4)

        # init individual maps
        self.one_char = mapper[char_maps[0]]
        self.two_char = mapper[char_maps[1]]
        self.three_char = mapper[char_maps[2]]
        self.four_char = mapper[char_maps[3]]

        # order from highest char compounds to single char
        self.all_dicts = [self.four_char, self.three_char, self.two_char, self.one_char]
        # filter out empty maps, i.e. None
        self.all_dicts = [i for i in self.all_dicts if i]

    def transcribe_ipa_word(self, word):
        # TODO: shutil copy is likely better
        word_copy = word * 1
        # parse trough mappers starting with highest character compounds
        for char_dict in self.all_dicts:
            for key in char_dict:
                value = char_dict[key]
                # map the character to LV letter or a placeholder in case of compounds
                word_copy = word_copy.replace(key, value)

        return word_copy

    def transcribe(self, sentence):
        # split sentence into words
        sentence = sentence.split()

        # transcribe each word
        tr_sentence = []
        for word in sentence:
            # convert English to IPA
            ipa_word = ipa.convert(word)
            # map IPA to Latvian
            tr_word = self.transcribe_ipa_word(ipa_word)
            tr_sentence.append(tr_word)

        return " ".join(tr_sentence)

    # for bash convenience


if __name__ == "__main__":
    import logging

    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)

    # test
    en_string = "the quick brown fox jumps over the lazy dog in the rhythm of the moonlight sonata"
    trs = Transcriber("ipa2lv_alphabet.yaml")
    res = trs.transcribe(en_string)
    logging.info("Input: %s" % en_string)
    logging.info("Output: %s" % res)
