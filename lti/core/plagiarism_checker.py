from lti.helpers import is_punctuation, tok_and_lem
from difflib import ndiff


class PlagiarismChecker:
    def __init__(self):
        pass

    def _get_matches(self, tokens1, tokens2):
        matches = []
        match = []
        index = -1
        min_length = 4

        for i, d in enumerate(ndiff(tokens1, tokens2)):
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

    def run(self, text, excerpt):
        text_lemmas = [s.lower() for s in tok_and_lem(text) if not is_punctuation(s)]
        excerpt_lemmas = [s.lower() for s in tok_and_lem(excerpt) if not is_punctuation(s)]

        return self._get_matches(text_lemmas, excerpt_lemmas)
