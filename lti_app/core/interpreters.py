"""Collection of interpreters for the raw data analysis."""

from django.template.loader import render_to_string

from lti_app import strings


semantics_similarity_low_threshold = 0.15
semantics_similarity_high_threshold = 0.35


class FeedbackInterpreter:
    """Interpreter for pilot/diagnostic assessments."""

    def __init__(self, semantics_threshold):
        self.semantics_threshold = (
            semantics_similarity_low_threshold
            if semantics_threshold == 1
            else semantics_similarity_high_threshold
        )

    def run(self, data):
        """Runs the interpreter.

        Args:
            data (dict): The raw data from the checker
            semantics_threshold (int): The semantics threshold
        """

        # Citation status
        # ---------------------------------------------
        cc = data.get(strings.citation_check)

        if cc is not None:
            data['citation_status'] = cc.get('result')

        # Grammar status
        # ---------------------------------------------
        gc = data.get(strings.grammar_check)

        if gc is not None:
            data['grammar_status'] = all([len(value) == 0 for value in gc.values()])

        # Academic style status
        # ---------------------------------------------
        asc = data[strings.academic_style_check]

        if asc is not None:
            data['academic_style_status'] = all([len(value) == 0 for value in asc.values()])

        # Paraphrase status
        # ---------------------------------------------
        pc = data.get(strings.plagiarism_check)
        sc = data.get(strings.semantics_check)
        code = ''

        if pc is not None:
            data['plagiarism_status'] = len(pc) == 0
            code += str(int(data['plagiarism_status']))
        else:
            code += 'N'

        if sc is not None:
            data['semantics_status'] = sc >= self.semantics_threshold
            code += str(int(data['semantics_status']))
        else:
            code += 'N'

        data['paraphrase_status'] = code


class GradeInterpreter:
    """Interpreter for graded assessments.

    Attributes:
        major_grammar_errors (list): The major grammar errors
            which may fail an assignment.

    Args:
        assignment_type (str): The assignment type.
    """

    major_grammar_errors = ['sentence_fragments', 'comma_splices']

    def __init__(self, assignment_type, semantics_threshold):
        self.assignment_type = assignment_type
        self.semantics_threshold = (
            semantics_similarity_low_threshold
            if semantics_threshold == 1
            else semantics_similarity_high_threshold
        )

    def _get_errors(self, d, exclude=None, include='*'):
        if exclude is None:
            exclude = []

        if d is None:
            return []

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

    def _get_minor_errors_aggregate(self, data, exclude=None):
        if exclude is None:
            exclude = []

        citation_check = data.get(strings.citation_check)
        grammar_check = data.get(strings.grammar_check)
        style_check = data.get(strings.academic_style_check)
        minor_errors = 0

        if citation_check is not None:
            minor_errors += (1 if citation_check.get('result') else 0)

        if grammar_check is not None:
            minor_errors += self._get_errors(
                grammar_check,
                exclude=list(set().union(self.major_grammar_errors, exclude))
            )

        if style_check is not None:
            minor_errors += self._get_errors(style_check)

        return minor_errors

    def _get_major_errors_aggregate(self, data):
        if data.get(strings.semantics_check) is not None:
            semantics_error = int(not data.get('semantics_status'))
        else:
            semantics_error = 0

        if data.get(strings.plagiarism_check) is not None:
            plagiarism_errors = len(data.get(strings.plagiarism_check))
        else:
            plagiarism_errors = 0

        if data.get(strings.grammar_check) is not None:
            major_grammar_errors = self._get_errors(
                data.get(strings.grammar_check),
                exclude='*',
                include=self.major_grammar_errors
            )
        else:
            major_grammar_errors = 0

        return semantics_error + plagiarism_errors + major_grammar_errors

    def _is_in_band_1(self, data):
        result = True

        # Grammar
        # ---------------------------------------------
        grammar_errors = self._get_errors(
            data.get(strings.grammar_check),
            exclude=self.major_grammar_errors
        )
        result = result and grammar_errors == 0

        # Academic style
        # ---------------------------------------------
        style_errors = self._get_errors(data.get(strings.academic_style_check))
        result = result and style_errors == 0

        # Citation
        # ---------------------------------------------
        if data.get(strings.citation_check) is not None:
            result = result and data.get(strings.citation_check)

        # Plagiarism
        # ---------------------------------------------
        if data.get(strings.plagiarism_check) is not None:
            result = result and len(data.get(strings.plagiarism_check) == 0)

        return result

    def _is_in_band_2(self, data):
        grammar_check = data.get(strings.grammar_check)
        style_check = data.get(strings.academic_style_check)

        grammar_errors = self._get_errors(
            grammar_check,
            exclude=self.major_grammar_errors
        )
        style_errors = self._get_errors(style_check)

        return grammar_errors == 1 or style_errors == 1

    def _is_in_band_3(self, data):
        citation_check = data.get(strings.citation_check)
        minor_errors = self._get_minor_errors_aggregate(
            data,
            exclude=[strings.citation_check]
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

        data['comments'] = render_to_string(strings.learner_canvas_feedback, {
            'band': band,
            'semantics_similarity_threshold': self.semantics_threshold,
            **data
        })
