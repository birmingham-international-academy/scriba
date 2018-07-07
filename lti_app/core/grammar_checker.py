"""Provides grammar checkers."""

import re
import os

import language_check
import spacy
import spellchecker
from nltk import ngrams, pos_tag, word_tokenize, WhitespaceTokenizer
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from nltk.tree import Tree
from spacy.matcher import Matcher

from lti_app.core.text_helpers import (
    clean_text, load_stanford_parser, TextProcessor
)
from lti_app.helpers import (
    contains_list, is_number, is_punctuation, remove_punctuation
)


class Checker(TextProcessor):
    """Implements the default grammar checker.

    Attributes:
        clause_types (list): A list of clause-level POS tags.
        transitive_verbs (list): A list of transitive verbs
            that require an object.

    Args:
        text: The text submitted by the student.
    """

    clause_types = ['S', 'SBAR', 'SINV', 'SQ']
    transitive_verbs = ['bring', 'cost', 'give', 'lend', 'offer',
                        'pass', 'play', 'read', 'send', 'sing', 'teach',
                        'write', 'buy', 'get', 'leave', 'make', 'owe',
                        'pay', 'promise', 'refuse', 'show', 'take', 'tell']

    def __init__(self, text):
        self.text = text
        TextProcessor.__init__(self)

    def _load_tools(self):
        self.parser, self.dependency_parser = load_stanford_parser()
        # self.nlp = spacy.load('en')
        self.spell = spellchecker.SpellChecker()
        self.spell.word_frequency.load_words(["we're", "you're", "won't"])
        self.languagetool = language_check.LanguageTool('en-GB')
        self.lemmatizer = WordNetLemmatizer()

    def _preprocess(self):
        self.text = clean_text(self.text)
        sentences = sent_tokenize(self.text)
        self.sentences = [
            sentence
            for line in list(self.parser.raw_parse_sents(sentences))
            for sentence in line
        ]

        for sentence in self.sentences:
            print(sentence)

        """
        sents = self.dependency_parser.raw_parse_sents(sentences)

        for line in sents:
            for sentence in line:
                print(list(sentence.triples()))
        """

    def _is_clause(self, node):
        return node.label() in self.clause_types

    def get_malformed_sentences(self, sentence):
        """Get malformed sentences.

        A sentence is malformed if it doesn't convey a "full" thought.

        Args:
            sentence (Tree): The parse tree of the sentence.

        Returns:
            list of str: The malformed sentences.
        """

        # Get clause types
        malformed = []
        subtrees = list(sentence.subtrees(filter=self._is_clause))

        # There is no sentence, this means it's malformed.
        if len(subtrees) == 0:
            return [' '.join(sentence.leaves())]

        for tree in subtrees:
            compounds = [node.label() for node in tree]

            # Not accepted compounds
            if (
                not contains_list(compounds, ['NP', 'VP'])
                and compounds != ['VP']
                and not contains_list(compounds, ['SBAR', 'VP'])
                and not contains_list(compounds, ['S', 'CC', 'S'])
                and not contains_list(compounds, ['IN', 'S'])
            ):
                malformed.append(tree.flatten())

        return [' '.join(malformed_str) for malformed_str in malformed]

    def get_comma_splices(self, sentence):
        """Get the comma splices in a sentence.

        A comma splice or comma fault is the use of a comma
        to join two independent clauses.

        Args:
            sentence (Tree): The parse three of the sentence.

        Returns:
            list of str: The comma splices.
        """

        subtrees = list(sentence.subtrees(filter=self._is_clause))
        comma_splices = []

        for tree in subtrees:
            compounds = [node.label() for node in tree]

            if 'CC' not in compounds and contains_list(compounds, ['S', ","]):
                comma_splices.append(tree.flatten())

        return [' '.join(token) for token in comma_splices]

    def get_noun_verb_disagreements(self, sentence):
        """Get noun-verb disagreements.

        Subject-verb disagreement is when you use the plural-form verb
        for a single-form noun as in "the fox play".

        Args:
            sentence (Tree): The parse tree of the sentence.

        Returns:
            list of str: Subject-verb disagreements.
        """

        def is_noun(n):
            return n.startswith('NN') or n == 'PRP'

        def is_verb(n):
            return n.startswith('VB')

        def has_disagreement(n_label, v_label):
            return (
                (n_label in ['NN', 'NNP'] and v_label == 'VBP')
                or (n_label in ['NNS', 'NNPS'] and v_label == 'VBZ')
                or (n_label in ['he', 'she', 'it'] and v_label == 'VBP')
                or (n_label in ['you', 'we', 'they'] and v_label == 'VBZ')
            )

        disagreements = []
        subtrees = list(sentence.subtrees(filter=self._is_clause))

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

    def get_run_ons(self, sentence):
        """Get run on/fused sentences.

        A run on sentence is a grammatically faulty sentence
        in which two or more main or independent clauses
        are joined without a word to connect them
        or a punctuation mark to separate them.

        Args:
            sentence (Tree): The parse tree of the sentence.

        Returns:
            list of str: The fused sentences.
        """

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

    def get_sentence_fragments(self, sentence):
        """Get sentence fragments.

        A sentence fragment is a sentence which
        doesn't have an independent clause.

        Args:
            sentence (Tree): The parse tree of the sentence.

        Returns:
            list of str: The sentence fragments found.
        """

        # Search for subtrees with POS tag == FRAG
        def is_frag(n): n.label() == 'FRAG'
        subtrees = list(sentence.subtrees(filter=is_frag))

        return [' '.join(node.leaves()) for node in subtrees]

    def get_transitive_verbs_without_object(self, sentence):
        """Get transitive verbs without a mandatory object.

        Args:
            sentence (Tree): The parse tree of the sentence.

        Returns:
            list of str: The transitive verbs without object.
        """

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

            if not has_object and verb in self.transitive_verbs:
                transitive_verbs_without_object.append(tree)

        return [
            ' '.join(node.leaves())
            for node in transitive_verbs_without_object
        ]

    def get_spelling_mistakes(self):
        """Get spelling mistakes.

        Returns:
            list of dict: A list of spelling mistake and corrections
        """

        # Tokenize text and ignore numbers.
        tokenizer = WhitespaceTokenizer()
        pattern = re.compile(r'^\(\d+\)$')
        words = [
            remove_punctuation(word.lower())
            for word in tokenizer.tokenize(self.text)
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

    def get_there_their_occurrences(self):
        """Get there-their mistakes such as 'there father is kind'.

        Returns:
            list of str: The occurrences of there-their mistakes.
        """
        """
        patterns = [
            [
                {'LOWER': 'there'},
                {'POS': 'ADV', 'OP': '?'},
                {'POS': 'ADJ', 'OP': '?'},
                {'POS': 'NOUN'},
                {'POS': 'VERB', 'OP': '?'}
            ]
        ]

        matcher_obj = Matcher(self.nlp.vocab)
        matcher_obj.add('THERE_THEIR', None, *patterns)

        doc = self.nlp(self.text)
        matches = matcher_obj(doc)
        """

        return []

        # return [doc[start:end] for _, start, end in matches]

    def get_to_too_occurrences(self):
        """Get to/too mistakes.

        Example: it's to hot.

        Returns:
            list of str: The occurrences of to-too mistakes.
        """
        pass

    def process_parse_tree(self, processors, key_function=None):
        """Process the parse tree for a sentence.

        Args:
            processors (list): List of functions taking a parse tree
                as an argument.
            key_function (function, optional): Defaults to None. Function
                to name the dictionary keys.

        Returns:
            dict: Mapping of the processors' results.
        """

        def default_key_function(fn_name, index):
            return '_'.join(fn_name.split('_')[1:])

        key_function = key_function or default_key_function

        data = {}

        for sentence in self.sentences:
            for index, processor in enumerate(processors):
                key = key_function(processor.__name__, index)
                result = processor(sentence)

                if data.get(key) is None:
                    data[key] = result
                else:
                    data[key].extend(result)

        return data

    def run(self, authors):
        """Run the grammar checker.

        Args:
            authors (list of str): The list of authors of the excerpt
                to exclude from spell checking.

        Returns:
            dict: The grammar check data using the described methods.
        """

        # Make the spell checker to ignore the author last names
        self.spell.word_frequency.load_words(authors + ["i'm"])

        data = {
            'spell_check': self.get_spelling_mistakes(),
            'languagetool_check': [
                entry
                for entry in self.languagetool.check(self.text)
                if entry.locqualityissuetype != 'misspelling'
            ],
            'there_their': self.get_there_their_occurrences()
        }

        # Process the parse tree sentences
        parse_tree_data = self.process_parse_tree([
            self.get_comma_splices,
            self.get_malformed_sentences,
            self.get_sentence_fragments,
            self.get_run_ons,
            self.get_transitive_verbs_without_object,
            self.get_noun_verb_disagreements,
        ])

        # print(parse_tree_data)

        parse_tree_data['sentence_fragments'] = (
            parse_tree_data.get('sentence_fragments', []) +
            parse_tree_data.get('malformed_sentences', [])[:]
        )
        parse_tree_data.pop('malformed_sentences', None)

        return {**data, **parse_tree_data}
