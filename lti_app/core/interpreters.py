"""Provides interpreters for the analysis data.

Todo:
    - GradeInterpreter -> grammar and/or style correct
    - Store settings
"""

from django.template.loader import render_to_string


semantics_similarity_threshold = 0.2


class FeedbackInterpreter:
    """Interpreter for pilot/diagnostic assessments."""

    def run(self, data):
        """Runs the interpreter.

        Args:
            data (dict): The raw data from the checker

        Returns:
            dict: The interpreted data to process in the templates.
        """

        # Grammar status
        gc = data['grammar_check']
        data['grammar_status'] = all([
            len(value) == 0
            for key, value in gc.items()
            if key != 'spell_check'
        ])

        # Spelling status
        data['spelling_status'] = len(gc['spell_check']) == 0

        # Academic style status
        asc = data['academic_style_check']
        data['academic_style_status'] = (
            len(asc['contractions']) == 0
            and len(asc['phrasal_verbs']) < 3
            and len(asc['general_informalities']) == 0
        )

        # Paraphrase status
        pc = data['plagiarism_check']
        sc = data['semantics_check']
        data['plagiarism_status'] = len(pc) == 0
        data['semantics_status'] = sc >= semantics_similarity_threshold

        return data


class GradeInterpreter:
    """Interpreter for graded assessments.

    Attributes:
        major_grammar_errors (list): The major grammar errors
            which may fail an assignment.

    Args:
        assignment_type (str): The assignment type.
    """

    major_grammar_errors = ['sentence_fragments', 'run_ons']

    def __init__(self, assignment_type):
        self.assignment_type = assignment_type

    def _get_errors(self, d, exclude=[], include='*'):
        keys = d.keys()
        exclude = keys if exclude == '*' else exclude
        include = keys if include == '*' else include
        include = set(include) - set(exclude)

        errors = [
            value
            for key, value in d.items()
            if key in include and len(value) > 0
        ]

        return len(errors)

    def _get_minor_errors_aggregate(self, data, exclude=[]):
        citation_check = data.get('citation_check')
        grammar_check = data.get('grammar_check')
        style_check = data.get('academic_style_check')

        minor_errors = self._get_errors(
            grammar_check,
            exclude=list(set().union(self.major_grammar_errors, exclude))
        )
        minor_errors += self._get_errors(style_check)
        minor_errors += (1 if citation_check.get('result') else 0)

        return minor_errors

    def _get_major_errors_aggregate(self, data):
        grammar_check = data.get('grammar_check')

        semantics_error = int(
            data.get('semantics_check') < semantics_similarity_threshold
        )

        plagiarism_errors = len(data.get('plagiarism_check'))

        major_grammar_errors = self._get_errors(
            grammar_check,
            exclude='*',
            include=self.major_grammar_errors
        )

        return semantics_error + plagiarism_errors + major_grammar_errors

    def _is_in_band_1(self, data):
        citation_check = data.get('citation_check')
        style_check = data.get('academic_style_check')
        grammar_check = data.get('grammar_check')
        plagiarism_check = data.get('plagiarism_check')

        grammar_errors = self._get_errors(
            grammar_check,
            exclude=self.major_grammar_errors
        )
        style_errors = self._get_errors(style_check)

        return (
            citation_check.get('result') is True
            and grammar_errors == 0
            and style_errors == 0
            and len(plagiarism_check) == 0
        )

    def _is_in_band_2(self, data):
        grammar_check = data.get('grammar_check')
        style_check = data.get('academic_style_check')

        grammar_errors = self._get_errors(
            grammar_check,
            exclude=self.major_grammar_errors
        )
        style_errors = self._get_errors(style_check)

        return grammar_errors == 1 or style_errors == 1

    def _is_in_band_3(self, data):
        citation_check = data.get('citation_check')
        minor_errors = self._get_minor_errors_aggregate(
            data,
            exclude=['citation_check']
        )

        return (
            minor_errors == 2
            or minor_errors == 3
            or not citation_check.get('result')
        )

    def _is_in_band_4(self, data):
        minor_errors = self._get_minor_errors_aggregate(data)
        major_errors = self._get_major_errors_aggregate(data)

        return minor_errors >= 4 or major_errors == 1

    def run(self, data):
        """Runs the interpreter.

        Args:
            data (dict): The raw data from the checker

        Returns:
            dict: The interpreted data to process in the templates.
        """

        if self.assignment_type == 'D':
            data['score'] = 0
            band = None
        elif self._is_in_band_4(data):
            data['score'] = 0
            band = 4
        elif self._is_in_band_3(data):
            data['score'] = 0.6
            band = 3
        elif self._is_in_band_2(data):
            data['score'] = 0.8
            band = 2
        elif self._is_in_band_1(data):
            data['score'] = 1
            band = 1

        data['comments'] = render_to_string('learner/canvas-feedback.html', {
            'band': band,
            'semantics_similarity_threshold': semantics_similarity_threshold,
            **data
        })

        return data
