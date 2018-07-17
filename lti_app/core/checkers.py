"""Provides the paraphrase analyzers."""

import logging

from lti_app.core import (
    academic_style_checker,
    citation_checker,
    grammar_checker,
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

        self.citation_checker = citation_checker.Checker(
            self.text,
            self.reference
        )
        self.academic_style_checker = academic_style_checker.Checker(
            self.text
        )
        self.semantics_checker = semantics_checker.Checker(
            self.text,
            self.excerpt,
            self.supporting_excerpts
        )
        self.grammar_checker = grammar_checker.Checker(
            self.text,
            deferred_preprocess=True
        )
        self.plagiarism_checker = plagiarism_checker.Checker(
            self.text,
            self.excerpt
        )

    def run(self):
        """Run the checker

        Returns:
            dict: The raw data from the analyzers described above.
        """

        # Citation check
        citation_check = self.citation_checker.run()

        # Academic style check
        academic_style_check = self.academic_style_checker.run()

        # Semantics check
        semantics_check = self.semantics_checker.run()

        # Plagiarism check
        plagiarism_check = self.plagiarism_checker.run()

        # Grammar check
        authors = citation_check.get('authors')
        self.grammar_checker._preprocess(authors=authors)
        grammar_check = self.grammar_checker.run()

        data = {
            'citation_check': citation_check,
            'academic_style_check': academic_style_check,
            'semantics_check': semantics_check,
            'grammar_check': grammar_check,
            'plagiarism_check': plagiarism_check
        }

        logger.debug('%s', data)

        return data
