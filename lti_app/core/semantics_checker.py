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
        self.parser, _ = load_stanford_parser()
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def _preprocess(self):
        self.text = clean_text(self.text)
        self.excerpt = clean_text(self.excerpt)

        self.text_sentences = sent_tokenize(self.text)
        self.excerpt_sentences = sent_tokenize(self.excerpt)

        self.pt_text_sentences = self.parser.raw_parse_sents(self.text_sentences)
        self.pt_excerpt_sentences = self.parser.raw_parse_sents(self.excerpt_sentences)

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

        self.text_pred_args = self._get_pred_patterns(
            self.pt_text_sentences,
            opts
        )
        self.excerpt_pred_args = self._get_pred_patterns(
            self.pt_excerpt_sentences,
            opts
        )

    def _get_pred_patterns(self, sentences, opts):
        pred_patt = []

        for line in sentences:
            for sentence in line:
                pp = PredPatt.from_constituency(str(sentence), opts=opts)
                # pp = PredPatt.from_sentence(sentence, opts=opts)
                for predicate in pp.instances:
                    pred_patt.append({
                        'target': predicate,
                        'args': predicate.arguments
                    })

        return pred_patt

    def _is_target_negated(self, target):
        tokens = [token.text for token in target.tokens]
        return 'not' in tokens or "n't" in tokens

    def _tuple_similarity(self, t1, t2):
        similarity = 0.0
        weight_target = 1.7
        weight_arg = 1
        num_args_shared = 0

        target1 = self.stemmer.stem(t1['target'].root.text)
        args1 = t1['args']

        target2 = self.stemmer.stem(t2['target'].root.text)
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
            arg1_text = arg1 and self.stemmer.stem(arg1.root.text)
            arg2_text = arg2 and self.stemmer.stem(arg2.root.text)

            if (
                arg1 is not None
                and arg2 is not None
                and (
                    arg1_text == arg2_text
                    or are_synonyms(arg1_text, arg2_text)
                )
            ):
                similarity += weight_arg
            num_args_shared += 1

        normalization_factor = weight_target + num_args_shared

        return round(similarity / normalization_factor, 2)

    def run(self):
        pairs = []
        text_pred_args = self.text_pred_args[:]
        excerpt_pred_args = self.excerpt_pred_args[:]

        # print(self.text_pred_args)
        # print(self.excerpt_pred_args)

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

        if len(pairs) == 0:
            return 0

        aggregate_result = sum([sim for _, _, sim in pairs]) / len(pairs)

        return aggregate_result
