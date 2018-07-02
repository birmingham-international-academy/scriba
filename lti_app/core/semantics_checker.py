"""Provides semantics checkers.

A semantic checker must detect the topic
as well as the semantic structure similarity.

Todo:
    - Single word synonyms
    - Compound word synonyms
    - Detect negations
    - Detect idioms
    - Different POS tags

"""

import itertools
import re
import os

import spacy
from gensim import corpora, models, similarities
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from predpatt import PredPatt, PredPattOpts
from predpatt.util.ud import dep_v1, dep_v2

from lti_app.helpers import (
    get_current_dir, find_file, tok_and_lem, is_punctuation
)
from lti_app.core.text_helpers import (
    are_synonyms, are_hierarchically_related,  clean_text,
    load_stanford_parser, TextProcessor
)


class Checker(TextProcessor):
    """Implements the default semantics checker.

    Args:
        text (str): The text submitted by the student.
        excerpt (str): The assignment's excerpt.
    """

    def __init__(self, text, excerpt):
        self.text = text
        self.excerpt = excerpt
        TextProcessor.__init__(self)

    def _load_tools(self):
        _, self.dependency_parser = load_stanford_parser()
        self.nlp = spacy.load('en')
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def _preprocess(self):
        self.text = clean_text(self.text)
        self.excerpt = clean_text(self.excerpt)

        self.text_sentences = sent_tokenize(self.text)
        self.excerpt_sentences = sent_tokenize(self.excerpt)

        # Create target-arguments tuples
        # ------------------------------

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

        self.text_pred_args = []
        self.excerpt_pred_args = []

        for text_sentence in self.text_sentences:
            pp = PredPatt.from_sentence(text_sentence, opts=opts)
            for predicate in pp.instances:
                self.text_pred_args.append({
                    'target': predicate,
                    'args': predicate.arguments
                })

        for excerpt_sentence in self.excerpt_sentences:
            pp = PredPatt.from_sentence(excerpt_sentence, opts=opts)
            for predicate in pp.instances:
                self.excerpt_pred_args.append({
                    'target': predicate,
                    'args': predicate.arguments
                })

    def _is_target_negated(self, target):
        tokens = [token.text for token in target.tokens]
        return 'not' in tokens or "n't" in tokens

    def _tuple_similarity(self, t1, t2):
        similarity = 0.0
        weight_target = 1.7
        weight_arg = 1
        num_args_shared = 0

        target1 = t1['target'].root.text
        args1 = t1['args']

        target2 = t2['target'].root.text
        args2 = t2['args']

        # Reverse arguments if passive voice is used
        if len(args1) == 2 and args1[0].root.gov_rel == 'nsubjpass':
            args1.reverse()

        if len(args2) == 2 and args2[0].root.gov_rel == 'nsubjpass':
            args2.reverse()

        # Check for negation in the predicate
        t1_negated = self._is_target_negated(t1['target'])
        t2_negated = self._is_target_negated(t2['target'])
        negation_mismatch = (
            (t1_negated and not t2_negated) or
            (not t1_negated and t2_negated)
        )

        if (
            not negation_mismatch and
            (target1 == target2 or are_synonyms(target1, target2))
        ):
            similarity += weight_target

        for arg1, arg2 in list(itertools.zip_longest(args1, args2)):
            if (
                arg1 is not None
                and arg2 is not None
                and (
                    arg1.root.text == arg2.root.text
                    or are_synonyms(arg1.root.text, arg2.root.text)
                )
            ):
                similarity += weight_arg
            num_args_shared += 1

        normalization_factor = weight_target + num_args_shared

        return similarity / normalization_factor

    def run(self):
        # print(self.text_dep_addr)
        # print(self.excerpt_dep_addr)

        similarity_threshold = 0.6
        pairs = []
        text_pred_args = self.text_pred_args[:]
        excerpt_pred_args = self.excerpt_pred_args[:]

        print(self.text_pred_args)
        print(self.excerpt_pred_args)

        while len(text_pred_args) > 0 and len(excerpt_pred_args) > 0:
            similarity_results = []

            for d_text in text_pred_args:
                for d_excerpt in excerpt_pred_args:
                    similarity = self._tuple_similarity(d_text, d_excerpt)
                    similarity_results.append((d_text, d_excerpt, similarity))

            best_pair = max(similarity_results, key=lambda item: item[2])

            if best_pair[2] > similarity_threshold:
                pairs.append(best_pair)

            text_pred_args.remove(best_pair[0])
            excerpt_pred_args.remove(best_pair[1])

        print(pairs)
