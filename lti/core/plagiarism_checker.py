from lti.helpers import is_punctuation, tok_and_lem
from nltk import ngrams


class PlagiarismChecker:
    def __init__(self):
        pass

    def _gram_hits(self, tokens1, tokens2, n):
        hits = []
        hit = False
        grams2 = ngrams(tokens2, n)

        for gram in ngrams(tokens1, n):
            if gram in grams2 and not hit:
                hits.append(gram)
                hit = True
            else:
                hit = False

        return hits

    def _search_word_strings(self, text, excerpt):
        text_lemmas = [s for s in tok_and_lem(text) if not is_punctuation(s)]
        excerpt_lemmas = [s for s in tok_and_lem(excerpt) if not is_punctuation(s)]
        hits = dict()

        hits['three_words'] = self._gram_hits(text_lemmas, excerpt_lemmas, 3)
        hits['four_words'] = self._gram_hits(text_lemmas, excerpt_lemmas, 4)
        hits['five_words'] = self._gram_hits(text_lemmas, excerpt_lemmas, 5)
        hits['six_words'] = self._gram_hits(text_lemmas, excerpt_lemmas, 6)

        return hits

    def run(self, text, excerpt):
        return self._search_word_strings(text, excerpt)
