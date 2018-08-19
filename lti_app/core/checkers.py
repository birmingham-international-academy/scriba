"""Provides the paraphrase analyzers."""

import copy

from lti_app import strings
from lti_app.core import (
    academic_style_checker,
    citation_checker,
    grammar_checker,
    plagiarism_checker,
    semantics_checker
)
from lti_app.core.text_processing import processing_graphs, processors


class DefaultChecker:
    """The default paraphrase analyzer.

    The deault checker runs checking for the following categories:
    - Citation: if Harvard citation is present.
    - Academic style: searches for informalities.
    -

    Args:
        text (str): The text submitted by the student.
        excerpt (str): The excerpt to paraphrase.
        supporting_excerpts (str): Paraphrase excerpts examples.
        reference (str): The reference to cite in the text.
    """

    default_checks = {
        'citation': True,
        'grammar': True,
        'plagiarism': True,
        'academic_style': True,
        'semantics': 1
    }

    def __init__(self, text, excerpt, supporting_excerpts, reference, checks=None):
        self.text = text
        self.excerpt = excerpt
        self.supporting_excerpts = supporting_excerpts
        self.reference = reference
        self.data = {}

        # Setup the checks to run
        # ---------------------------------------------
        if checks is None:
            self.checks = self.default_checks.copy()
        else:
            self.checks = checks.copy()

        # Run text processor
        # ---------------------------------------------

        # Run citation checker in advance in order to
        # clean the text from citations
        self.citation_checker = citation_checker.Checker(
            self.text,
            self.reference
        )

        processing_graph = copy.deepcopy(processing_graphs.default_graph)

        # If the citation check is enabled...
        if (
            self.checks.get('citation')
            and self.reference is not None
            and self.reference != ''
        ):
            # ... use the citation remover as the root
            self.data[strings.citation_check] = self.citation_checker.run()
            root = processing_graphs.citation_remover
        else:
            # ... otherwise use the standard text cleaner
            root = processing_graphs.text_cleaner

        # Instantiate the text processor
        self.text_processor = processors.TextProcessor(
            processing_graph,
            root
        )

        # Submitted text processing
        self.text_document = self.text_processor.run(
            self.text,
            citation_check=self.data.get(strings.citation_check),
            enable_cache=False
        )

        # Excerpt text processing
        self.text_processor.graph_root = processing_graphs.text_cleaner
        self.excerpt_document = self.text_processor.run(
            self.excerpt,
            enable_cache=True
        )

        # Initialize checkers
        # -------------------
        self.academic_style_checker = academic_style_checker.Checker(
            self.text_document
        )
        self.semantics_checker = semantics_checker.Checker(
            self.text_document,
            self.excerpt_document,
            self.supporting_excerpts,
            enable_cache=True
        )
        self.grammar_checker = grammar_checker.Checker(
            self.text_document
        )
        self.plagiarism_checker = plagiarism_checker.Checker(
            self.text_document,
            self.excerpt_document
        )

    def run(self):
        """Run the checker

        Returns:
            dict: The raw data from the analyzers described above.
        """

        # Academic style check
        if self.checks.get('academic_style'):
            self.data[strings.academic_style_check] = self.academic_style_checker.run()

        # Semantics check
        if self.checks.get('semantics') > 0:
            self.data[strings.semantics_check] = self.semantics_checker.run()

        # Plagiarism check
        if self.checks.get('plagiarism'):
            self.data[strings.plagiarism_check] = self.plagiarism_checker.run()

        # Grammar check
        if self.checks.get('grammar'):
            self.data[strings.grammar_check] = self.grammar_checker.run()

        return self.data
