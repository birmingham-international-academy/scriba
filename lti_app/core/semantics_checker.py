"""Provides semantics checkers.

A semantic checker must detect the topic
as well as the semantic structure similarity.

Todo:
    - Compound word synonyms
    - Detect idioms
    - Different POS tags

"""

import hashlib
import itertools
import re
from functools import wraps

from django.core.cache import cache
from gensim import corpora, models, similarities
from nltk import word_tokenize
from predpatt import PredPatt

from lti_app import strings
from lti_app.caching import Cache, caching
from lti_app.core.text_helpers import are_synonyms, clean_text, is_punctuation
from lti_app.core.text_processing.tools import Tools


class Checker:
    """Implements the default semantics checker.

    Args:
        text_document (Document): The text submitted by the student.
        excerpt_document (Document): The assignment's excerpt.
        supporting_excerpts (str): Paraphrase excerpts examples.
    """

    def __init__(
        self,
        text_document,
        excerpt_document,
        supporting_excerpts,
        use_cache=False
    ):
        self.text_document = text_document
        self.excerpt_document = excerpt_document

        if supporting_excerpts is None:
            self.supporting_excerpts = []
        elif type(supporting_excerpts) is list:
            self.supporting_excerpts = supporting_excerpts
        elif type(supporting_excerpts) is str:
            self.supporting_excerpts = [
                line.strip()
                for line in clean_text(supporting_excerpts).splitlines()
                if line.strip() != ''
            ]

        self.cache = Cache(
            enabled=use_cache,
            base_key=self.excerpt_document.text + ''.join(self.supporting_excerpts)
        )

        # Load document vectors
        documents = [self.excerpt_document.text] + self.supporting_excerpts
        self.dictionary, self.vectors_corpus = self._docs_to_vectors(documents)

        # Load tools
        self.tools = Tools()

    @caching('docs_to_vectors')
    def _docs_to_vectors(self, documents):
        def tokenize_document(document):
            stoplist = set('for a of the and to in'.split())

            return [
                word
                for word in word_tokenize(document.lower())
                if word not in stoplist and not is_punctuation(word)
            ]

        texts = [
            tokenize_document(document)
            for document in documents
        ]

        dictionary = corpora.Dictionary(texts)

        return dictionary, [dictionary.doc2bow(text) for text in texts]

    @caching('matrix_similarity')
    def _load_matrix_similarity(self):
        tfidf = models.TfidfModel(self.vectors_corpus)
        index = similarities.SparseMatrixSimilarity(
            tfidf[self.vectors_corpus],
            num_features=len(self.dictionary)
        )

        return tfidf, index

    def _is_target_negated(self, target):
        tokens = [token.text for token in target.tokens]
        return 'not' in tokens or "n't" in tokens

    def _tuple_similarity(self, t1, t2):
        """
        resolve_relcl = True    # relative clauses
        resolve_appos = True    # appositional modifiers
        resolve_amod = True     # adjectival modifiers
        resolve_conj = True     # conjuction
        resolve_poss = True     # possessives
        """

        similarity = 0.0
        weights = {
            'target': {
                'appos': 0.4,
                'amod': 0.3,
                'conj': 0.6
            },
            'argument': 1
        }
        default_weight_target = 1.3
        num_args_shared = 0

        # Get Targets and Arguments
        # ---------------------------------------------

        target1 = self.tools.stemmer.stem(t1['target'].root.text)
        args1 = t1['args']

        target2 = self.tools.stemmer.stem(t2['target'].root.text)
        args2 = t2['args']

        # Target Similarity
        # ---------------------------------------------

        # Check for negation in the predicate
        t1_negated = self._is_target_negated(t1['target'])
        t2_negated = self._is_target_negated(t2['target'])
        negation_mismatch = (
            (t1_negated and not t2_negated) or
            (not t1_negated and t2_negated)
        )

        # Calculate similarity
        target1_gov_rel = t1['target'].root.gov_rel
        target2_gov_rel = t2['target'].root.gov_rel
        if (
            not negation_mismatch
            and target1_gov_rel == target2_gov_rel
            and (target1 == target2 or are_synonyms(target1, target2))
        ):
            similarity += (
                weights.get('target').get(target1_gov_rel)
                or default_weight_target
            )

        # Arguments Similarity
        # ---------------------------------------------

        # Reverse arguments if passive voice is used
        if len(args1) == 2 and args1[0].root.gov_rel == 'nsubjpass':
            args1.reverse()

        if len(args2) == 2 and args2[0].root.gov_rel == 'nsubjpass':
            args2.reverse()

        # Calculate similarity
        for arg1, arg2 in list(itertools.zip_longest(args1, args2)):
            arg1_text = arg1 and self.tools.stemmer.stem(arg1.root.text)
            arg2_text = arg2 and self.tools.stemmer.stem(arg2.root.text)

            if (
                arg1 is not None
                and arg2 is not None
                and (
                    arg1_text == arg2_text
                    or are_synonyms(arg1_text, arg2_text)
                )
            ):
                similarity += weights.get('argument')
            num_args_shared += 1

        normalization_factor = default_weight_target + num_args_shared

        return round(similarity / normalization_factor, 2)

    def run(self):
        # 1. Predicate patterns method
        # ---------------------------------------------

        pairs = []
        text_pred_args = self.text_document.get(strings.predicate_patterns)[:]
        excerpt_pred_args = self.excerpt_document.get(strings.predicate_patterns)[:]

        while len(text_pred_args) > 0 and len(excerpt_pred_args) > 0:
            similarity_results = []

            for d_text in text_pred_args:
                for d_excerpt in excerpt_pred_args:
                    similarity = self._tuple_similarity(d_text, d_excerpt)
                    similarity_results.append((d_text, d_excerpt, similarity))

            best_pair = max(similarity_results, key=lambda item: item[2])

            pairs.append(best_pair)

            text_pred_args.remove(best_pair[0])
            excerpt_pred_args.remove(best_pair[1])

        print(excerpt_pred_args)

        if len(pairs) == 0:
            pp_method_result = 0.0
        else:
            pp_method_result = sum([sim for _, _, sim in pairs]) / len(pairs)

        # 2. Vector similarity method
        # ---------------------------------------------

        tfidf, index = self._load_matrix_similarity()

        tokens = [
            token.lower()
            for token in self.text_document.get(strings.tokens)
            if not is_punctuation(token)
        ]
        vec = self.dictionary.doc2bow(tokens)

        sims = index[tfidf[vec]]

        vs_method_result = sum(sims) / len(sims)

        if vs_method_result == 0.0 and len(self.supporting_excerpts) == 0:
            pp_method_result *= 1.3

        # if vs_method_result == 0.0 and len(self.supporting_excerpts) == 0:
        #    overall_result = pp_method_result
        # else:
        #    overall_result = (pp_method_result + vs_method_result) / 2

        print(pp_method_result)
        print(vs_method_result)

        return max(vs_method_result, pp_method_result)
