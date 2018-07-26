import re

import spacy
from nltk import pos_tag, tokenize
from nltk.tokenize import sent_tokenize
from predpatt import PredPatt, PredPattOpts
from predpatt.util.ud import dep_v1

from lti_app.core.exceptions import PipelineException
from lti_app.core.text_helpers import clean_text, is_punctuation
from lti_app.core.tools import Tools


text_pipeline = [
    {'name': 'citation_remover', 'out': 'cleaned_text'},
    {'name': 'sent_tokenizer', 'out': 'sentences'},
    {'name': 'parser', 'out': 'parse_tree'},
    {'name': 'predicate_patterns_matcher', 'out': 'predicate_patterns'},
    {'name': 'word_tokenizer', 'out': 'tokens'},
    {'name': 'pos_tagger', 'out': 'tagged_tokens'},
    {'name': 'lemmatizer', 'out': 'lemmas'},
    {'name': 'spacy_processor', 'out': 'spacy_doc'}
]

excerpt_pipeline = [
    {'name': 'clean_text', 'out': 'cleaned_text'},
    {'name': 'sent_tokenizer', 'out': 'sentences'},
    {'name': 'parser', 'out': 'parse_tree'},
    {'name': 'predicate_patterns_matcher', 'out': 'predicate_patterns'},
    {'name': 'word_tokenizer', 'out': 'tokens'},
    {'name': 'pos_tagger', 'out': 'tagged_tokens'},
    {'name': 'lemmatizer', 'out': 'lemmas'}
]


class Document:
    def __init__(self, text):
        self.text = text
        self.data = {}

    def get(self, key, d=None):
        return self.data.get(key, d)

    def add_data(self, name, data):
        self.data[name] = data


class Pipeline:
    def __init__(self, text, pipeline):
        self.text = text
        self.pipeline = pipeline
        self.tools = Tools()

    def _clean_text(self, document, args={}):
        return clean_text(document.text)

    def _citation_remover(self, document, args={}):
        authors = args.get('authors')
        year = args.get('year')

        pattern = (
            r'\((.*?(?:'
            + re.escape(str(authors[0]))
            + r'|'
            + re.escape(str(year))
            + r').*?)\)'
        )
        paren_chunks = [
            m.span()
            for m in re.finditer(pattern, document.text)
        ]

        text = document.text

        if len(paren_chunks) > 0:
            indexes = list(sum(paren_chunks, ()))
            text_copy = document.text[:indexes[0]]

            for i in range(1, len(indexes) - 1, 2):
                index_start = indexes[i]
                index_end = indexes[i + 1]

                text_copy += document.text[index_start:index_end]

            text_copy += document.text[indexes[len(indexes) - 1]:]

            text = text_copy

        return clean_text(text)

    def _sent_tokenizer(self, document, args={}):
        cleaned_text = document.get('cleaned_text')

        if cleaned_text is None:
            raise PipelineException()

        return sent_tokenize(document.get('cleaned_text'))

    def _parser(self, document, args={}):
        sentences = document.get('sentences')

        if sentences is None:
            raise PipelineException()

        return [
            sentence
            for line in self.tools.parser.raw_parse_sents(sentences)
            for sentence in line
        ]

    def _get_pred_patterns(self, sentences, opts):
        pred_patt = []

        for sentence in sentences:
            pp = PredPatt.from_constituency(str(sentence), opts=opts)
            for predicate in pp.instances:
                pred_patt.append({
                    'target': predicate,
                    'args': predicate.arguments
                })

        return pred_patt

    def _predicate_patterns_matcher(self, document, args={}):
        resolve_relcl = True  # relative clauses
        resolve_appos = True  # appositional modifiers
        # resolve_amod = True   # adjectival modifiers
        resolve_conj = True   # conjuction
        resolve_poss = True   # possessives
        ud = dep_v1.VERSION   # the version of UD
        opts = PredPattOpts(
            resolve_relcl=resolve_relcl,
            resolve_appos=resolve_appos,
            # resolve_amod=resolve_amod,
            resolve_conj=resolve_conj,
            resolve_poss=resolve_poss,
            ud=ud
        )
        parse_tree = document.get('parse_tree')

        if parse_tree is None:
            raise PipelineException()

        return self._get_pred_patterns(
            parse_tree,
            opts
        )

    def _word_tokenizer(self, document, args={}):
        cleaned_text = document.get('cleaned_text')

        if cleaned_text is None:
            raise PipelineException()

        return tokenize.word_tokenize(cleaned_text)

    def _pos_tagger(self, document, args={}):
        tokens = document.get('tokens')

        if tokens is None:
            raise PipelineException()

        return pos_tag(tokens)

    def _lemmatizer(self, document, args={}):
        tagged_tokens = document.get('tagged_tokens')

        if tagged_tokens is None:
            raise PipelineException()

        return [
            self.tools.lemmatizer.lemmatize(i, j[0].lower())
            if j[0].lower() in ['a', 'n', 'v']
            else self.tools.lemmatizer.lemmatize(i)
            for i, j in tagged_tokens
            if not is_punctuation(i)
        ]

    def _spacy_processor(self, document, args={}):
        cleaned_text = document.get('cleaned_text')

        if cleaned_text is None:
            raise PipelineException()

        return self.tools.nlp(cleaned_text)

    def run(self, args={}):
        document = Document(self.text)

        for action in self.pipeline:
            action_name = action.get('name')
            out_name = action.get('out')

            action = getattr(self, '_' + action_name)
            data = action(document, args)

            document.add_data(out_name, data)

        return document
