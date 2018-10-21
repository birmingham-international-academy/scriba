"""Components processing raw text."""


import hashlib
import re
from functools import wraps

from django.core.cache import cache
from nltk.tokenize import sent_tokenize
from predpatt import PredPatt, PredPattOpts
from predpatt.util.ud import dep_v1

from .tools import Tools
from lti_app import strings
from lti_app.caching import Cache, caching
from lti_app.core.exceptions import TextProcessingException
from lti_app.core.text_helpers import clean_text, is_punctuation
from lti_app.helpers import chunks, flatten


# Processing Nodes
# =============================================

class ProcessorNode:
    """Base class for nodes in a text processing graph."""

    def __init__(self, **kwargs):
        self.attrs = kwargs
        self.tools = Tools()
        self.cache = None

    def __eq__(self, other):
        return self.attrs == other.attrs

    def __hash__(self):
        return hash(str(self.attrs))

    def _process(self, **kwargs):
        raise NotImplementedError()

    def process(self, **kwargs):
        """Process the text."""

        document = kwargs.get('document')
        enable_cache = kwargs.get('enable_cache')

        self.cache = Cache(
            enabled=enable_cache,
            base_key=document.text
        )

        return self._process(**kwargs)


class TextCleaner(ProcessorNode):
    def __init__(self, name='text_cleaner', out=strings.cleaned_text):
        ProcessorNode.__init__(self, name=name, out=out)

    @caching(['attrs', 'name'])
    def _process(self, **kwargs):
        document = kwargs.get('document')
        return clean_text(document.text)


class CitationRemover(ProcessorNode):
    def __init__(self, name='citation_remover', out=strings.cleaned_text):
        ProcessorNode.__init__(self, name=name, out=out)

    @caching(['attrs', 'name'])
    def _process(self, **kwargs):
        document = kwargs.get('document')
        citation_check = kwargs.get(strings.citation_check)

        if citation_check is None and type(citation_check) is not dict:
            raise TextProcessingException.missing_key(strings.citation_check)

        authors = citation_check.get('authors')
        year = citation_check.get('year')

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


class SentenceTokenizer(ProcessorNode):
    def __init__(self, name='sentence_tokenizer', out=strings.sentences):
        ProcessorNode.__init__(self, name=name, out=out)

    @caching(['attrs', 'name'])
    def _process(self, **kwargs):
        document = kwargs.get('document')
        input_key = kwargs.get('input_key')
        cleaned_text = document.get(input_key)

        if cleaned_text is None:
            raise TextProcessingException.missing_key(input_key)

        return sent_tokenize(cleaned_text)


class Parser(ProcessorNode):
    def __init__(self, name='parser', out=strings.parse_data):
        ProcessorNode.__init__(self, name=name, out=out)

    @caching(['attrs', 'name'])
    def _process(self, **kwargs):
        document = kwargs.get('document')
        input_key = kwargs.get('input_key')
        text = document.get(input_key)

        if text is None:
            raise TextProcessingException.missing_key(input_key)

        return self.tools.parser.parse(text)


class PredicatePatternsMatcher(ProcessorNode):
    def __init__(
        self,
        name='predicate_patterns_matcher',
        out=strings.predicate_patterns
    ):
        ProcessorNode.__init__(self, name=name, out=out)

    def _get_pred_patterns(self, sentences, opts):
        pred_patt = []

        for sentence in sentences:
            pp = PredPatt.from_constituency(str(sentence), opts=opts, cacheable=False)

            for predicate in pp.instances:
                pred_patt.append({
                    'target': predicate,
                    'args': predicate.arguments
                })

        return pred_patt

    @caching(['attrs', 'name'])
    def _process(self, **kwargs):
        document = kwargs.get('document')
        input_key = kwargs.get('input_key')

        resolve_relcl = True    # relative clauses
        resolve_appos = True    # appositional modifiers
        resolve_amod = True     # adjectival modifiers
        resolve_conj = True     # conjuction
        resolve_poss = True     # possessives
        ud = dep_v1.VERSION     # the version of UD
        opts = PredPattOpts(
            resolve_relcl=resolve_relcl,
            resolve_appos=resolve_appos,
            resolve_amod=resolve_amod,
            resolve_conj=resolve_conj,
            resolve_poss=resolve_poss,
            ud=ud
        )
        parse_tree = document.get(input_key)

        if parse_tree is None:
            raise TextProcessingException.missing_key(input_key)

        constituencies = parse_tree.get(strings.constituencies)
        return self._get_pred_patterns(constituencies, opts)


class Stemmer(ProcessorNode):
    def __init__(self, name='stemmer', out=strings.stems):
        ProcessorNode.__init__(self, name=name, out=out)

    @caching(['attrs', 'name'])
    def _process(self, **kwargs):
        document = kwargs.get('document')
        input_key = kwargs.get('input_key')
        parse_data = document.get(input_key)

        if parse_data is None:
            raise TextProcessingException.missing_key(input_key)

        tagged_tokens = flatten(parse_data.get(strings.tagged_tokens))

        return [
            (token.get('word'), self.tools.stemmer.stem(token.get('word')))
            for token in tagged_tokens
            if not is_punctuation(token.get('word'))
        ]


# Register Processing Nodes
# =============================================

text_cleaner = TextCleaner()
citation_remover = CitationRemover()
sentence_tokenizer = SentenceTokenizer()
parser = Parser()
predicate_patterns_matcher = PredicatePatternsMatcher()
stemmer = Stemmer()


# Processing Graphs
# =============================================

default_graph = {
    text_cleaner: [parser],
    citation_remover: [parser],
    parser: [predicate_patterns_matcher, stemmer],
    predicate_patterns_matcher: [],
    stemmer: []
}
