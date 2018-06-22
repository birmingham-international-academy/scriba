from lti.helpers import is_punctuation, tok_and_lem
from difflib import ndiff


class PlagiarismChecker:
    def __init__(self, text, excerpt):
        self.text = text
        self.excerpt = excerpt
        self._preprocess()

    def _preprocess(self):
        def get_lemmas(text):
            return [
                s.lower()
                for s in tok_and_lem(self.text)
                if not is_punctuation(s)
            ]

        self.text_lemmas = get_lemmas(self.text)
        self.excerpt_lemmas = get_lemmas(self.excerpt)

    def get_matches(self):
        matches = []
        match = []
        index = -1
        min_length = 4

        for i, d in enumerate(ndiff(self.text_lemmas, self.excerpt_lemmas)):
            if d[0] == ' ':
                word = d.split(' ')[-1]

                if i == index + 1:
                    match.append(word)
                else:
                    if len(match) >= min_length:
                        matches.append(' '.join(match))
                    match = [word]

                index = i

        if len(match) >= min_length:
            matches.append(' '.join(match))

        return matches

    def run(self):
        return self.get_matches()
