import os
import re
import language_check
import spacy
from spacy.matcher import Matcher
from lti_app.helpers import is_punctuation, remove_punctuation, is_number
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk import word_tokenize, WhitespaceTokenizer
from nltk.tokenize import sent_tokenize
from nltk.tree import Tree
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from .text_helpers import load_stanford_parser


class GrammarChecker:
    CLAUSE_TYPES = ['S', 'SINV', 'SQ']
    TRANSITIVE_VERBS = ['bring', 'cost', 'give', 'lend', 'offer',
                        'pass', 'play', 'read', 'send', 'sing', 'teach',
                        'write', 'buy', 'get', 'leave', 'make', 'owe',
                        'pay', 'promise', 'refuse', 'show', 'take', 'tell']

    def __init__(self, text):
        self.text = text
        self._load_tools()
        self._preprocess()

    def _load_tools(self):
        self.parser, self.dependency_parser = load_stanford_parser()
        self.nlp = spacy.load('en')
        self.spell = SpellChecker()
        self.spell.word_frequency.load_words(["we're", "you're", "won't"])
        self.languagetool = language_check.LanguageTool('en-GB')
        self.lemmatizer = WordNetLemmatizer()

    def _preprocess(self):
        sentences = sent_tokenize(self.text)
        self.text = self.text.strip()
        self.text = re.sub(' +', ' ', self.text)
        self.sentences = list(self.parser.raw_parse_sents(sentences))

    @staticmethod
    def _is_valid_subordinating_conj_clause(node):
        return 'IN' in [child.label() for child in node]

    @staticmethod
    def _is_clause_component(node):
        sbar = node.label() == 'SBAR'
        valid_scc = GrammarChecker._is_valid_subordinating_conj_clause(node)

        return type(node) is Tree\
            and node.label() in ['SBAR', 'NP', 'VP', 'S', 'CC']\
            and (valid_scc if sbar else True)

    def get_sentence_fragments(self, sentence):
        def is_frag(n): n.label() == 'FRAG'
        subtrees = list(sentence.subtrees(filter=is_frag))

        return [' '.join(node.leaves()) for node in subtrees]

    def get_malformed_sentences(self, sentence):
        def is_clause(n): n.label() in GrammarChecker.CLAUSE_TYPES
        malformed = []
        subtrees = list(sentence.subtrees(filter=is_clause))

        if len(subtrees) == 0:
            return [' '.join(sentence.leaves())]

        for tree in subtrees:
            compounds = [
                node.label()
                for node in tree
                if self._is_clause_component(node)
            ]
            compounds = sorted(compounds)

            if (
                not set(['NP', 'VP']).issubset(compounds)
                and compounds != ['VP']
                and compounds != ['SBAR', 'VP']
                and compounds != ['CC', 'S', 'S']
            ):
                malformed.append(tree.flatten())

        return [' '.join(malformed_str) for malformed_str in malformed]

    def get_run_ons(self, sentence):
        def filter(n):
            found_sentence = False
            found_sub_conj = False

            for c in n:
                if type(c) is Tree:
                    if c.label() == 'S':
                        found_sentence = True
                    if c.label() == 'IN':
                        found_sub_conj = True

            return n.label() == 'SBAR'\
                and found_sentence\
                and not found_sub_conj

        subtrees = list(sentence.subtrees(filter=filter))

        return [' '.join(node.leaves()) for node in subtrees]

    def get_transitive_verbs_without_object(self, sentence):
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() == 'VP'))
        transitive_verbs_without_object = []

        for tree in subtrees:
            verb = ''
            has_object = False

            for node in tree:
                if node.label().startswith('VB'):
                    verb = self.lemmatizer.lemmatize(node[0].lower(), 'v')

                if node.label() == 'NP':
                    has_object = True

            if not has_object and verb in GrammarChecker.TRANSITIVE_VERBS:
                transitive_verbs_without_object.append(tree)

        return [
            ' '.join(node.leaves())
            for node in transitive_verbs_without_object
        ]

    def get_noun_verb_disagreements(self, sentence):

        def is_clause(n): n.label() in GrammarChecker.CLAUSE_TYPES

        def is_noun(n): n.startswith('NN') or n == 'PRP'

        def is_verb(n): n.startswith('VB')

        def has_disagreement(n_label, v_label):
            return (
                (n_label in ['NN', 'NNP'] and v_label == 'VBP')
                or (n_label in ['NNS', 'NNPS'] and v_label == 'VBZ')
                or (n_label in ['he', 'she', 'it'] and v_label == 'VBP')
                or (n_label in ['you', 'we', 'they'] and v_label == 'VBZ')
            )

        disagreements = []
        subtrees = list(sentence.subtrees(filter=is_clause))

        for tree in subtrees:
            noun_phrase = None
            verb_phrase = None

            for node in tree:
                if node.label() == 'NP':
                    noun_phrase = node
                elif node.label() == 'VP':
                    verb_phrase = node

            if noun_phrase is None or verb_phrase is None:
                continue

            base_noun = [n for n in noun_phrase if is_noun(n.label())]
            base_verb = [v for v in verb_phrase if is_verb(v.label())]

            if base_noun == [] or base_verb == []:
                continue

            noun, noun_label = base_noun[0], base_noun[0].label()
            verb, verb_label = base_verb[0], base_verb[0].label()
            phrase = noun[0] + ' ' + verb[0]

            if has_disagreement(noun_label, verb_label):
                disagreements.append(phrase)

            if noun_label == 'PRP':
                pronoun = noun[0].lower()

                if has_disagreement(pronoun, verb_label):
                    disagreements.append(phrase)

        return disagreements

    def get_there_their_occurrences(self, text):
        patterns = [
            [
                {'LOWER': 'there'},
                {'POS': 'ADV', 'OP': '?'},
                {'POS': 'ADJ', 'OP': '?'},
                {'POS': 'NOUN'},
                {'POS': 'VERB', 'OP': '?'}
            ]
        ]

        matcher = Matcher(self.nlp.vocab)
        matcher.add('THERE_THEIR', None, *patterns)

        doc = self.nlp(text)
        matches = matcher(doc)

        return [doc[start:end] for _, start, end in matches]

    def get_spelling_mistakes(self, text):
        tokenizer = WhitespaceTokenizer()
        pattern = re.compile(r'^\(\d+\)$')
        words = [
            remove_punctuation(word.lower())
            for word in tokenizer.tokenize(text)
        ]
        words = [
            word
            for word in words
            if word != ''
            and not is_number(word)
            and pattern.match(word) is None
        ]

        mapped_words = []
        for word in words:
            parts = word.split("'")

            if len(parts) == 2 and (parts[1] == 's' or parts[1] == ''):
                mapped_words.append(parts[0])
            else:
                mapped_words.append(word)

        return [
            {'word': word, 'corrections': self.spell.candidates(word)}
            for word in self.spell.unknown(mapped_words)
        ]

    def run(self, authors):
        self.spell.word_frequency.load_words(authors)

        data = {
            'malformed_sentences': [],
            'sentence_fragments': [],
            'run_ons': [],
            'transitive_verbs_without_object': [],
            'noun_verb_disagreements': [],
            'spell_check': None,
            'languagetool_check': [
                entry
                for entry in self.languagetool.check(self.text)
                if entry.locqualityissuetype != 'misspelling'
            ],
            'there_their': self.get_there_their_occurrences(self.text)
        }

        def process_sentence(sentence):
            print(sentence)

            data['malformed_sentences'].extend(
                self.get_malformed_sentences(sentence)
            )
            data['sentence_fragments'].extend(
                self.get_sentence_fragments(sentence)
            )
            data['run_ons'].extend(
                self.get_run_ons(sentence)
            )
            data['transitive_verbs_without_object'].extend(
                self.get_transitive_verbs_without_object(sentence)
            )
            data['noun_verb_disagreements'].extend(
                self.get_noun_verb_disagreements(sentence)
            )
            data['spell_check'] = self.get_spelling_mistakes(
                self.text
            )

        for line in self.sentences:
            for sentence in line:
                process_sentence(sentence)

        return data
