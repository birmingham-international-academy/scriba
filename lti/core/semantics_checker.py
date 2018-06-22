import os
from lti.helpers import get_current_dir, find_file, tok_and_lem, is_punctuation
from nltk import pos_tag
from nltk.parse.stanford import StanfordDependencyParser
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet as wn
from gensim import corpora, models, similarities
import spacy
from .text_helpers import load_stanford_parser


class SemanticsChecker:
    def __init__(self, text, excerpt):
        self.text = text
        self.excerpt = excerpt
        self._load_tools()

    def _load_tools(self):
        _, self.dependency_parser = load_stanford_parser()
        self.nlp = spacy.load('en')

    def _word_similarity(self, w1, w2):
        pass

    def run(self):
        text_doc = self.nlp(self.text)
        excerpt_doc = self.nlp(self.excerpt)
        print(text_doc.similarity(excerpt_doc))

        """text_sentences =  self.dependency_parser.raw_parse_sents(sent_tokenize(text))
        excerpt_sentences = self.dependency_parser.raw_parse_sents(sent_tokenize(text))

        for sentence in text_sentences:
            for line in sentence:
                print(line)
        """
        # Sentence similarity
        #text_lemmas = pos_tag([s for s in tok_and_lem(text) if not is_punctuation(s)])
        #excerpt_lemmas = pos_tag([s for s in tok_and_lem(excerpt) if not is_punctuation(s)])

        """stoplist = set('for a of the and to in . , : " \''.split())
        documents = [excerpt, 'Candy (2017) wrote that his meta-analysis of over 50 studies showed that many people have too much salt in their diet and that this problem is causing health problems.']
        texts = [[word for word in word_tokenize(document.lower()) if word not in stoplist] for document in documents]

        dictionary = corpora.Dictionary(texts)
        num_features = len(dictionary)

        corpus = [dictionary.doc2bow(text) for text in texts]

        tfidf = models.TfidfModel(corpus)

        index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=num_features)

        text_vec = dictionary.doc2bow(word_tokenize(text.lower()))

        sims = index[tfidf[text_vec]]

        print(list(enumerate(sims)))"""


