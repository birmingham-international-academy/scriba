from nltk import pos_tag, tokenize
from nltk.stem import WordNetLemmatizer
from lti.helpers import get_current_dir
import spacy
import json
import os


class AcademicStyleChecker:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.nlp = spacy.load('en')

    def _search_phrasal_verbs(self, doc):
        phrasal_verbs = []

        for token in doc:
            if token.dep_ == 'prt' and token.head.pos_ == 'VERB':
                verb = token.head.orth_
                particle = token.orth_
                phrasal_verbs.append(verb + ' ' + particle)

        return phrasal_verbs

    def _search_contractions(self, tokens):
        return [tokens[index - 1] + token for index, token in enumerate(tokens) if "'" in token]

    def _search_general_informalities(self, lemmas):
        current_dir = get_current_dir(__file__)
        filename = os.path.join(current_dir, 'data', 'informal.json')

        with open(filename, 'r') as f:
            informal_words = json.load(f)

            return [word for word in informal_words if word.get('entity') in lemmas]

    def run(self, text):
        tokens = tokenize.word_tokenize(text)
        lemmas = [self.lemmatizer.lemmatize(i, j[0].lower())
                if j[0].lower() in
                ['a', 'n', 'v']
                else self.lemmatizer.lemmatize(i)
                for i, j in pos_tag(tokens)]
        doc = self.nlp(text)

        phrasal_verbs = self._search_phrasal_verbs(doc)
        contractions = self._search_contractions(tokens)
        general_informalities = self._search_general_informalities(' '.join(lemmas))

        return {
            'phrasal_verbs': phrasal_verbs,
            'contractions': contractions,
            'general_informalities': general_informalities
        }
