"""Provides interpreters for the analysis data.

Todo:
    - Fix comments
    - Add plagiarism check band
    - Add semantics check band
    - Store settings
"""


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
        data['grammar_status'] = (
            len(gc['malformed_sentences']) == 0
            and len(gc['languagetool_check']) == 0
            and len(gc['run_ons']) == 0
            and len(gc['transitive_verbs_without_object']) == 0
            and len(gc['sentence_fragments']) == 0
            and len(gc['noun_verb_disagreements']) == 0
            and len(gc['there_their']) == 0
        )

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
        data['paraphrase_status'] = len(pc) == 0

        return data


class GradeInterpreter:
    """Interpreter for graded assessments.

    Attributes:
        major_grammar_errors (list): The major grammar errors
            which may fail an assignment.

    Args:
        points_possible (int): Possible points for the assignment.
    """

    major_grammar_errors = ['sentence_fragments', 'malformed_sentences']

    def __init__(self, points_possible):
        self.points_possible = points_possible

    def _points_to_decimal_score(self, points):
        return points / self.points_possible

    def _decimal_to_points_score(self, decimal):
        return decimal * self.points_possible

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

        return self._get_errors(
            grammar_check,
            exclude='*',
            include=self.major_grammar_errors
        )

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

        if self._is_in_band_4(data):
            data['score'] = 0
            data['comments'] = 'The submission requires tutor guidance.'
        elif self._is_in_band_3(data):
            data['score'] = 0.6
            data['comments'] = 'You did OK.'
        elif self._is_in_band_2(data):
            data['score'] = 0.8
            data['comments'] = 'You did good!'
        elif self._is_in_band_1(data):
            data['score'] = 1
            data['comments'] = 'You did great man!\nKeep up the great work!'

        return data
