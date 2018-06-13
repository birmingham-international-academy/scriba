import os
from lti.helpers import get_current_dir, find_file
from nltk.parse.stanford import StanfordParser, StanfordDependencyParser
from nltk.tokenize import sent_tokenize
from nltk.tree import Tree
from nltk.stem import WordNetLemmatizer

class GrammarChecker:
    CLAUSE_TYPES = ['S', 'SINV', 'SQ']
    TRANSITIVE_VERBS = ['bring', 'cost', 'give', 'lend', 'offer', 'pass', 'play', 'read', 'send', 'sing', 'teach',\
                        'write', 'buy', 'get', 'leave', 'make', 'owe', 'pay', 'promise', 'refuse', 'show', 'take', 'tell']

    def __init__(self):
        stanford_parser_directory = os.path.join(get_current_dir(__file__), 'data', 'stanford-parser')
        parser_jar_filename = os.path.join(stanford_parser_directory, 'stanford-parser.jar')
        models_jar_filename = find_file('stanford-parser-*-models.jar', stanford_parser_directory)[0]
        self.parser = StanfordParser(parser_jar_filename, models_jar_filename)
        self.dependency_parser = StanfordDependencyParser(parser_jar_filename, models_jar_filename)

    @staticmethod
    def _is_valid_subordinating_conj_clause(node):
        return 'IN' in [child.label() for child in node]

    @staticmethod
    def _is_clause_component(node):
        return\
            type(node) is Tree\
            and node.label() in ['SBAR', 'NP', 'VP', 'S', 'CC']\
            and (GrammarChecker._is_valid_subordinating_conj_clause(node) if node.label() == 'SBAR' else True)

    def _traverse_parse_tree(self, tree, action):
        for node in tree:
            action(tree.label(), node)

            if isinstance(node, Tree):
                self._traverse_parse_tree(node, action)

    def _search_sentence_fragments(self, sentence):
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() == 'FRAG'))

        return [' '.join(node.leaves()) for node in subtrees]

    def _search_malformed_sentences(self, sentence):
        malformed = []
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() in GrammarChecker.CLAUSE_TYPES))

        if len(subtrees) == 0:
            return [' '.join(sentence.leaves())]

        for node in subtrees:
            compounds = [child.label() for child in node if GrammarChecker._is_clause_component(child)]
            compounds = sorted(compounds)

            if compounds != ['NP', 'VP'] and compounds != ['SBAR', 'VP'] and compounds != ['CC', 'S', 'S']:
                malformed.append(node.flatten())

        return [' '.join(malformed_str) for malformed_str in malformed]

    def _search_run_ons(self, sentence):
        def filter(n):
            sentence_present = False
            subordinating_conjuction_present = False

            for c in n:
                if type(c) is Tree:
                    if c.label() == 'S':
                        sentence_present = True
                    if c.label() == 'IN':
                        subordinating_conjuction_present = True

            return n.label() == 'SBAR' and sentence_present and not subordinating_conjuction_present

        subtrees = list(sentence.subtrees(filter=filter))

        return [' '.join(node.leaves()) for node in subtrees]

    def _search_transitive_verbs_without_object(self, sentence):
        lemmatizer = WordNetLemmatizer()

        subtrees = list(sentence.subtrees(filter=lambda n: n.label() == 'VP'))
        transitive_verbs_without_object = []

        for tree in subtrees:
            verb = ''
            has_object = False

            for node in tree:
                if node.label().startswith('VB'):
                    verb = lemmatizer.lemmatize(node[0].lower(), 'v')

                if node.label() == 'NP':
                    has_object = True

            if not has_object and verb in GrammarChecker.TRANSITIVE_VERBS:
                transitive_verbs_without_object.append(tree)

        return [' '.join(node.leaves()) for node in transitive_verbs_without_object]

    def _search_dangling_modifiers(self):
        pass

    def _search_noun_verb_disagreements(self, sentence):
        disagreements = []
        subtrees = list(sentence.subtrees(filter=lambda n: n.label() in GrammarChecker.CLAUSE_TYPES))

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

            base_noun = [n for n in noun_phrase if n.label().startswith('NN') or n.label() == 'PRP']
            base_verb = [n for n in verb_phrase if n.label().startswith('VB')]

            if base_noun == [] or base_verb == []:
                continue

            noun, noun_label = base_noun[0], base_noun[0].label()
            _, verb_label = base_verb[0], base_verb[0].label()
            phrase = ' '.join(tree.leaves())

            if noun_label in ['NN', 'NNP'] and verb_label == 'VBP':
                disagreements.append(phrase)

            if noun_label in ['NNS', 'NNPS'] and verb_label == 'VBZ':
                disagreements.append(phrase)

            if noun_label == 'PRP':
                pronoun = noun[0].lower()

                if (pronoun in ['he', 'she', 'it'] and verb_label == 'VBP') or (pronoun in ['you', 'we', 'they'] and verb_label == 'VBZ'):
                    disagreements.append(phrase)

        return disagreements

    def run(self, text):
        sentences = list(self.parser.raw_parse_sents(sent_tokenize(text)))
        data = {
            'malformed_sentences': [],
            'sentence_fragments': [],
            'run_ons': [],
            'transitive_verbs_without_object': [],
            'noun_verb_disagreements': []
        }

        for line in sentences:
            for sentence in line:
                print(sentence)
                data['malformed_sentences'].extend(self._search_malformed_sentences(sentence))
                data['sentence_fragments'].extend(self._search_sentence_fragments(sentence))
                data['run_ons'].extend(self._search_run_ons(sentence))
                data['transitive_verbs_without_object'].extend(self._search_transitive_verbs_without_object(sentence))
                data['noun_verb_disagreements'].extend(self._search_noun_verb_disagreements(sentence))

        #sentences = list(self.dependency_parser.raw_parse_sents(sent_tokenize(text)))

        #for line in sentences:
        #    for sentence in line:
        #        print(sentence.to_dot())

        return data
