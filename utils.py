import re
import string


# non alphabetical character filter
# does not filter punctuation by default
# filters out "-" for compound words

class AlphaFilter:
    def __init__(self):

        # ascii is default
        alphabet = "abcdefghijklmnopqrstuvwxyz"

        # ignore punctuation
        quotmarks = '\'`‘’"“”„‹›«»'
        dashes = '‒–—―‐-'
        brackets = '()\[\]{}⟨⟩'
        punct = '\.,:;!?…/⁄' + quotmarks + brackets + dashes
        self.rx_punct = re.compile(r'^[%s]|\.\.\.$' % punct)
        self.rx_alpha = re.compile(r'[^%s]' % alphabet, re.I)

    def process(self, tokens):
        # join input
        tokens = tokens.replace(" ", "")

        for t in tokens:

            # ignore most of punctuation
            if self.rx_alpha.match(t) and not self.rx_punct.match(t) and t not in string.punctuation:
                # ignore "_" (not part of regex)
                # do not ignore numbers this time
                return True

            # discard compound words
            elif t == "-":
                return True

            else:
                continue

        return False
