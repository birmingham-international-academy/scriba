"""Provides the paraphrase analyzers."""

from lti_app.core import (
    academic_style_checker,
    citation_checker,
    grammar_checker,
    plagiarism_checker,
    semantics_checker
)


class DefaultChecker:
    """The default paraphrase analyzer.

    The deault checker runs checking for the following categories:
    - Citation: if Harvard citation is present.
    - Academic style: searches for informalities.
    -

    Args:
        text (str): The text submitted by the student.
        excerpt (str): The excerpt to paraphrase.
        reference (str): The reference to cite in the text.
    """

    def __init__(self, text, excerpt, reference):
        self.text = text
        self.excerpt = excerpt
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
            self.excerpt
        )
        self.grammar_checker = grammar_checker.Checker(
            self.text
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

        citation_check = self.citation_checker.run()
        academic_style_check = self.academic_style_checker.run()
        semantics_check = self.semantics_checker.run()
        grammar_check = self.grammar_checker.run(citation_check.get('authors'))
        plagiarism_check = self.plagiarism_checker.run()

        return {
            'citation_check': citation_check,
            'academic_style_check': academic_style_check,
            'semantics_check': semantics_check,
            'grammar_check': grammar_check,
            'plagiarism_check': plagiarism_check
        }
