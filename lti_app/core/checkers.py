"""Provides the paraphrase analyzers."""

import logging

from lti_app.core import (
    academic_style_checker,
    citation_checker,
    grammar_checker,
    pipelines,
    plagiarism_checker,
    semantics_checker
)
from lti_app.setup_logging import setup_logging


logger = logging.getLogger(__name__)
setup_logging()


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

    def __init__(self, text, excerpt, supporting_excerpts, reference):
        self.text = text
        self.excerpt = excerpt
        self.supporting_excerpts = supporting_excerpts
        self.reference = reference
        self.data = {}

        # Run citation checker in advance
        # for pipeline preprocessing
        # -------------------------------
        self.citation_checker = citation_checker.Checker(
            self.text,
            self.reference
        )
        self.data['citation_check'] = self.citation_checker.run()

        # Run text pipeline
        # -----------------
        self.text_pipeline = pipelines.Pipeline(
            self.text,
            pipelines.text_pipeline
        )
        self.text_document = self.text_pipeline.run(
            args=self.data.get('citation_check')
        )

        # Run excerpt pipeline
        # --------------------
        self.excerpt_pipeline = pipelines.Pipeline(
            self.excerpt,
            pipelines.excerpt_pipeline
        )
        self.excerpt_document = self.excerpt_pipeline.run()

        # Initialize checkers
        # -------------------
        self.academic_style_checker = academic_style_checker.Checker(
            self.text_document
        )
        self.semantics_checker = semantics_checker.Checker(
            self.text_document,
            self.excerpt_document,
            self.supporting_excerpts
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
        self.data['academic_style_check'] = self.academic_style_checker.run()

        # Semantics check
        self.data['semantics_check'] = self.semantics_checker.run()

        # Plagiarism check
        self.data['plagiarism_check'] = self.plagiarism_checker.run()

        # Grammar check
        self.data['grammar_check'] = self.grammar_checker.run()

        logger.debug('%s', self.data)

        return self.data
