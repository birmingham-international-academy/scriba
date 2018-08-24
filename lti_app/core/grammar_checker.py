"""Provides grammar checkers."""

import re
import string

from nltk import WhitespaceTokenizer
from nltk.tree import ParentedTree

from lti_app import strings
from lti_app.core.text_helpers import clean_text, remove_punctuation
from lti_app.core.text_processing.tools import Tools
from lti_app.helpers import flatten


class Checker:
    """Implements the default grammar checker.

    Attributes:
        clause_types (list): A list of clause-level POS tags.

    Args:
        text_document (Document): The text submitted by the student.
    """

    clause_types = ['S', 'SBAR', 'SINV', 'SQ']

    def __init__(self, text_document):
        self.text_document = text_document
        self.tools = Tools()
        self.detokenize = self.tools.word_detokenizer.detokenize

    def _get_node_label(self, node):
        return node if type(node) is str else node.label()

    def _get_nouns(self, noun_phrase):
        nouns = []
        has_conjunction = False

        for node in noun_phrase:
            if type(node) is str:
                continue

            if self._is_noun(node.label()):
                nouns.append(node)
            elif node.label() == 'CC':
                has_conjunction = True
            else:
                nns, has_conj = self._get_nouns(node)

                nouns.extend(nns)
                has_conjunction = has_conjunction and has_conj

        return nouns, has_conjunction

    def _get_verbs(self, verb_phrase):
        verbs = []

        for node in verb_phrase:
            if isinstance(node, ParentedTree) and node.label() not in self.clause_types:
                if self._is_verb(node.label()):
                    verbs.append(node)
                else:
                    verbs.extend(self._get_verbs(node))

        return verbs

    def _has_disagreement(self, base_noun, base_verb, has_conjunction):
        noun_labels = [noun.label() for noun in base_noun]
        verb_labels = [verb.label() for verb in base_verb]

        if len(noun_labels) > 1 and has_conjunction:
            # Plural noun phrase (e.g. John and Mary)
            i_pronoun = False
            singular = False
            plural = True
        else:
            # Extract head noun (covers compound nouns)
            n_label = noun_labels[-1]

            if n_label == 'PRP':
                n_label = base_noun[0][0].lower()

            i_pronoun = n_label == 'i'
            singular = n_label in ['NN', 'NNP', 'he', 'she', 'it']
            plural = n_label in ['NNS','NNPS', 'you', 'we', 'they']

        return any([
            (
                (singular and verb_label == 'VBP')
                or (i_pronoun and verb_label == 'VBZ')
                or (plural and verb_label == 'VBZ')
            )
            for verb_label in verb_labels
        ])

    def _has_wh_clause(self, node):
        for child in node:
            label = self._get_node_label(child)

            if label.startswith('WH'):
                return True

        return False

    def _is_clause(self, node):
        return node.label() in self.clause_types

    def _is_noun(self, n):
        return n.startswith('NN') or n == 'PRP'

    def _is_verb(self, n):
        return n.startswith('VB')

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
            return [
                clean_text(self.detokenize(node.leaves()))
                for node in subtrees
            ]

        # Search for malformed sentences
        malformed = []
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() == 'S'))

        # There is no sentence, this means it's malformed.
        if len(subtrees) == 0:
            sent = sentence.leaves()
            return [clean_text(self.detokenize(sent))]

        for tree in subtrees:
            compounds = ' '.join([self._get_node_label(node) for node in tree])

            if (
                re.search(r'VP|ADJP|CONJP|PP', compounds) is None
                and re.search(r'SBAR VP', compounds) is None
                and re.search(r'S( CC S)+', compounds) is None
                and re.search(r'S( ; S)+', compounds) is None
            ):
                malformed.append(tree.flatten())

        return [
            clean_text(self.detokenize(malformed_str))
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
                or re.search(r'NP( VP)? , NP( VP)?', compounds) is not None
                or re.search(r'S( , S)+', compounds) is not None
            ):
                comma_splices.append(tree.flatten())

        # Find verb phrases with patterns: VP , VP , ...
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() == 'VP'))

        for tree in subtrees:
            compounds = ' '.join([node.label() for node in tree])

            if re.search(r'VP( , VP)+', compounds) is not None:
                comma_splices.append(tree.flatten())

        return [clean_text(self.detokenize(token)) for token in comma_splices]

    def get_noun_verb_disagreements(self, sentence):
        """Get noun-verb disagreements.

        Subject-verb disagreement is when you use the plural-form verb
        for a single-form noun as in "the fox play".

        Note:
            Does not catch: (S (VP (VBP give) (NP (JJ good) (NNS results))))

        Args:
            sentence (Tree): The parse tree of the sentence.

        Returns:
            list of str: Subject-verb disagreements.
        """

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

            # Get base noun components
            base_nouns, has_conjunction = self._get_nouns(noun_phrase)

            # Get base verb components
            base_verbs = self._get_verbs(verb_phrase)

            if base_nouns == [] or base_verbs == []:
                continue

            if self._has_disagreement(base_nouns, base_verbs, has_conjunction):
                phrase = self.detokenize(
                    noun_phrase.leaves() + verb_phrase.leaves()
                )
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
        raise NotImplementedError()

    def get_spelling_mistakes(self):
        """Get spelling mistakes.

        Note:
            DEPRECATED

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
        text = self.text_document.get(strings.cleaned_text)
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

    def get_countability_mistakes(self):
        """Get countability mistakes.

        Example: I installed (the) system.

        Returns:
            list of str: The occurrences of countability mistakes.
        """
        raise NotImplementedError()

    def get_auxiliary_do_negated_mistakes(self):
        """Get the auxiliary verb "do" (in negated form) mistakes.

        Example: They don't plagiarism. (It should be followed by another verb)

        Returns:
            list of str: The occurrences of the auxiliary "do" mistakes.
        """

        mistakes = []
        parse_data = self.text_document.get(strings.parse_data)
        tagged_tokens = flatten(parse_data.get(strings.tagged_tokens))
        len_tagged_tokens = len(tagged_tokens)

        for index, token in enumerate(tagged_tokens):
            token_word = token.get('word')

            if token_word == 'do' or token_word == 'did':
                next_token = None
                next_next_token = None

                if index + 1 < len_tagged_tokens:
                    next_token = tagged_tokens[index + 1]
                if index + 2 < len_tagged_tokens:
                    next_next_token = tagged_tokens[index + 2]

                next_token_word = (
                    next_token.get('word')
                    if next_token is not None
                    else ''
                )

                if (
                    (next_token_word == 'not' or next_token_word == "n't")
                    and next_next_token is not None
                    and not next_next_token.get('pos').startswith('VB')
                ):
                    token_word = token.get('word')
                    next_next_token_word = next_next_token.get('word')

                    mistake = token_word
                    mistake += (' ' if next_token_word == 'not' else '')
                    mistake += next_token_word
                    mistake += ' {}'.format(next_next_token_word)
                    mistakes.append(mistake)

        return mistakes

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
            for sentence in self.text_document.get(strings.parse_data).get(strings.constituencies)
        ]

        for sentence in sentences:
            for index, processor in enumerate(processors):
                key = key_function(processor.__name__, index)
                result = processor(sentence)

                if data.get(key) is None:
                    data[key] = result
                else:
                    data[key].extend(result)

        return data

    def languagetool_check_post_process(self, lt_check):
        # Remove proper nouns from spell check
        # ---------------------------------------------
        new_lt_check = []

        for mistake in lt_check:
            context = mistake.get('context')
            offset = context.get('offset')
            length = context.get('length')
            mistake_str = context.get('text')[offset:offset + length]

            if (
                mistake.get('rule').get('category').get('id') == 'TYPOS'
                and mistake_str[0].isupper()
            ):
                continue

            new_lt_check.append(mistake)

        return new_lt_check

    def run(self):
        """Run the grammar checker.

        Returns:
            dict: The grammar check data using the described methods.
        """

        cleaned_text = self.text_document.get(strings.cleaned_text)

        lt_check = self.tools.languagetool.check(cleaned_text)
        lt_check = self.languagetool_check_post_process(lt_check)
        auxiliary_do_negated_mistakes = self.get_auxiliary_do_negated_mistakes()

        data = {
            'languagetool_check': lt_check,
            'auxiliary_do_negated_mistakes': auxiliary_do_negated_mistakes
        }

        # Process the parse tree sentences
        parse_tree_data = self.process_parse_tree([
            self.get_comma_splices,
            self.get_sentence_fragments,
            self.get_noun_verb_disagreements,
        ])

        return {**data, **parse_tree_data}
