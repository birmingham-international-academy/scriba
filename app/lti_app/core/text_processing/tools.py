import spellchecker
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sacremoses import MosesDetokenizer

from lti_app.caching import caching
from lti_app.core.api import LanguageToolClient
from lti_app.core.text_processing.parser import Parser
from lti_app.helpers import Singleton


class Tools(metaclass=Singleton):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.parser = Parser()
        self.languagetool = LanguageToolClient()
        self.spell = spellchecker.SpellChecker()
        self.spell.word_frequency.load_words(["we're", "you're", "won't"])
        self.word_detokenizer = MosesDetokenizer()
