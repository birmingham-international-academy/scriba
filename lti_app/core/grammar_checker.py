"""Provides grammar checkers.

Todo:
    - Remove citation

"""

import re
import string

import spellchecker
from nltk import WhitespaceTokenizer
from nltk.tree import ParentedTree
from spacy.matcher import Matcher

from lti_app.core import languagetool
from lti_app.core.text_helpers import clean_text
from lti_app.core.tools import Tools
from lti_app.helpers import remove_punctuation


class Checker:
    """Implements the default grammar checker.

    Attributes:
        clause_types (list): A list of clause-level POS tags.
        transitive_verbs (list): A list of transitive verbs
            that require an object.

    Args:
        text_document (Document): The text submitted by the student.
    """

    clause_types = ['S', 'SBAR', 'SINV', 'SQ']
    transitive_verbs = ['bring', 'cost', 'give', 'lend', 'offer',
                        'pass', 'play', 'send', 'sing', 'teach',
                        'buy', 'get', 'leave', 'make', 'owe',
                        'pay', 'promise', 'refuse', 'show', 'take', 'tell']

    def __init__(self, text_document):
        self.text_document = text_document
        self.tools = Tools()

    def _is_clause(self, node):
        return node.label() in self.clause_types

    def _get_node_label(self, node):
        return node if type(node) is str else node.label()

    def _has_wh_clause(self, node):
        for child in node:
            label = self._get_node_label(child)

            if label.startswith('WH'):
                return True

        return False

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
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() == 'FRAG'))

        if len(subtrees) > 0:
            return [clean_text(' '.join(node.leaves())) for node in subtrees]

        # Search for malformed sentences
        malformed = []
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() == 'S'))

        # There is no sentence, this means it's malformed.
        if len(subtrees) == 0:
            return [clean_text(' '.join(sentence.leaves()))]

        for tree in subtrees:
            compounds = ' '.join([self._get_node_label(node) for node in tree])

            if (
                re.search(r'VP', compounds) is None
                and re.search(r'SBAR VP', compounds) is None
                and re.search(r'S( CC S)+', compounds) is None
                and re.search(r'S( ; S)+', compounds) is None
            ):
                malformed.append(tree.flatten())

        return [
            clean_text(' '.join(malformed_str))
            for malformed_str in malformed
        ]

    def get_comma_splices(self, sentence):
        """Get the comma splices in a sentence.

        A comma splice or comma fault is the use of a comma
        to join two independent clauses.

        Args:
            sentence (Tree): The parse three of the sentence.

        Returns:
            list of str: The comma splices.
        """

        comma_splices = []

        # Find clauses with patterns: S , NP VP | S , S , ...
        subtrees = list(sentence.subtrees(filter=self._is_clause))

        for tree in subtrees:
            compounds = ' '.join([node.label() for node in tree])

            if (
                re.search(r'S , NP VP', compounds) is not None
                or re.search(r'S( , S)+', compounds) is not None
            ):
                comma_splices.append(tree.flatten())

        # Find verb phrases with patterns: VP , VP , ...
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() == 'VP'))

        for tree in subtrees:
            compounds = ' '.join([node.label() for node in tree])

            if re.search(r'VP( , VP)+', compounds) is not None:
                comma_splices.append(tree.flatten())

        return [clean_text(' '.join(token)) for token in comma_splices]

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

        pass

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
                n = node.label()

                if n.startswith('VB'):
                    verb = self.tools.lemmatizer.lemmatize(node[0].lower(), 'v')

                if n == 'NP' or (n == 'SBAR' and self._has_wh_clause(node)):
                    has_object = True

            if not has_object and verb in self.transitive_verbs:
                transitive_verbs_without_object.append(tree)

        return [
            clean_text(' '.join(node.leaves()))
            for node in transitive_verbs_without_object
        ]

    def get_spelling_mistakes(self):
        """Get spelling mistakes.

        Returns:
            list of dict: A list of spelling mistake and corrections
        """

        # Tokenize text:
        # - Ignore numbers
        # - Ignore proper nouns
        # - Add spacing around parenthetical sections
        # - Remove unnecessary spaces
        tokenizer = WhitespaceTokenizer()
        number_pattern = re.compile(r'^\(\d+\)|\d+\w{2}|\d+$')
        contraction_pattern = re.compile(r'^.*\'(t|ve|ll|d)$')
        proper_noun_pattern = re.compile(r'^[A-Z].*$')
        text = self.text_document.get('cleaned_text')
        text = re.sub(r'([\(\)\[\]\{\}\'"])', r' \g<1> ', text)
        text = re.sub(' +', ' ', text)
        text = re.sub('\n+', ' ', text)

        words = [
            remove_punctuation(word)
            for word in tokenizer.tokenize(text)
        ]
        words = [
            word.lower()
            for word in words
            if word != ''
            and number_pattern.match(word) is None
            and contraction_pattern.match(word) is None
            and proper_noun_pattern.match(word) is None
            and word not in string.punctuation
        ]

        mapped_words = []
        for word in words:
            parts = word.split("'")

            if len(parts) == 2 and (parts[1] == 's' or parts[1] == ''):
                mapped_words.append(parts[0])
            else:
                mapped_words.append(word)

        return [
            {'word': word, 'corrections': self.tools.spell.candidates(word)}
            for word in self.tools.spell.unknown(mapped_words)
        ]

    def get_there_their_occurrences(self):
        """Get there-their mistakes such as 'there father is kind'.

        Returns:
            list of str: The occurrences of there-their mistakes.
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

        matcher_obj = Matcher(self.tools.nlp.vocab)
        matcher_obj.add('THERE_THEIR', None, *patterns)

        doc = self.text_document.get('spacy_doc')
        matches = matcher_obj(doc)

        return [doc[start:end] for _, start, end in matches]

    def get_countability_mistakes(self):
        """Get countability mistakes.

        Example: I installed (the) system.

        Returns:
            list of str: The occurrences of countability mistakes.
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

        sentences = [
            ParentedTree.fromstring(str(sentence))
            for sentence in self.text_document.get('parse_tree')
        ]

        for sentence in sentences:

            print(sentence)

            for index, processor in enumerate(processors):
                key = key_function(processor.__name__, index)
                result = processor(sentence)

                if data.get(key) is None:
                    data[key] = result
                else:
                    data[key].extend(result)

        return data

    def run(self):
        """Run the grammar checker.

        Returns:
            dict: The grammar check data using the described methods.
        """

        cleaned_text = self.text_document.get('cleaned_text')

        data = {
            'spell_check': self.get_spelling_mistakes(),
            'languagetool_check': languagetool.check(cleaned_text),
            'there_their': self.get_there_their_occurrences()
        }

        # Process the parse tree sentences
        parse_tree_data = self.process_parse_tree([
            self.get_comma_splices,
            self.get_sentence_fragments,
            self.get_noun_verb_disagreements,
        ])

        return {**data, **parse_tree_data}
