import spacy
import spellchecker
from nltk.stem import PorterStemmer, WordNetLemmatizer

from lti_app.helpers import Singleton
from lti_app.core.text_helpers import load_stanford_parser


class Tools(metaclass=Singleton):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.nlp = spacy.load('en')
        self.parser, self.dependency_parser = load_stanford_parser()
        self.spell = spellchecker.SpellChecker()
        self.spell.word_frequency.load_words(["we're", "you're", "won't"])
