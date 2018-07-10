"""Provides interpreters for the analysis data.

Todo:
    - Fix comments
    - Store settings
    - Use HTML library to build comments
"""

semantics_similarity_threshold = 0.6


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
            len(gc['languagetool_check']) == 0
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
        data['plagiarism_status'] = len(pc) == 0
        data['semantics_status'] = sc >= semantics_similarity_threshold

        return data


class GradeInterpreter:
    """Interpreter for graded assessments.

    Attributes:
        major_grammar_errors (list): The major grammar errors
            which may fail an assignment.

    Args:
        points_possible (int): Possible points for the assignment.
    """

    major_grammar_errors = ['sentence_fragments', 'run_ons']

    def __init__(self, points_possible):
        self.points_possible = points_possible

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

    def _render_html_list(self, ls, fn=lambda item: str(item)):
        html = '<ul>'
        for item in ls:
            html += '<li>' + fn(item) + '</li>'
        html += '</ul>'

        return html

    def _to_html(self, data):
        # Paraphrase
        html = '<h3>Paraphrase</h3>'
        check_status =\
            data['semantics_check'] >= semantics_similarity_threshold

        html += '<p>'
        if check_status:
            html += 'Your paraphrase reflects the correct meaning.'
        else:
            html += 'Your paraphrase does not reflect the correct meaning.'
        html += '</p>'

        plagiarism_check = data['plagiarism_check']
        if len(plagiarism_check) > 0:
            html += '<p>You may have copied the following words/phrases:</p>'
            html += self._render_html_list(plagiarism_check)
        else:
            html += '<p>Good job! You have not copied substantial content from the original text.</p>'

        # Grammar
        grammar_check = data['grammar_check']
        html += '<h3>Grammar</h3>'
        no_grammar_errors = True

        if len(grammar_check['run_ons']) > 0:
            no_grammar_errors = False
            html += '<p>The following run ons have been found:</p>'
            html += self._render_html_list(grammar_check['run_ons'])

        if len(grammar_check['comma_splices']) > 0:
            no_grammar_errors = False
            html += '<p>The following comma splices have been found:</p>'
            html += self._render_html_list(grammar_check['comma_splices'])

        if len(grammar_check['sentence_fragments']) > 0:
            no_grammar_errors = False
            html += '<p>The following sentence fragments have been found:</p>'
            html += self._render_html_list(grammar_check['sentence_fragments'])

        if len(grammar_check['transitive_verbs_without_object']) > 0:
            no_grammar_errors = False
            html += '<p>The following transitive verbs without object have been found:</p>'
            html += self._render_html_list(grammar_check['transitive_verbs_without_object'])

        if len(grammar_check['there_their']) > 0:
            no_grammar_errors = False
            html += '<p>The following there/their mistakes have been found:</p>'
            html += self._render_html_list(grammar_check['there_their'])

        if len(grammar_check['noun_verb_disagreements']) > 0:
            no_grammar_errors = False
            html += '<p>The following noun-verb disagreements have been found:</p>'
            html += self._render_html_list(grammar_check['noun_verb_disagreements'])

        if len(grammar_check['languagetool_check']) > 0:
            no_grammar_errors = False
            html += '<p>The following noun-verb disagreements have been found:</p>'
            html += self._render_html_list(grammar_check['languagetool_check'], lambda mistake: mistake['message'] + ': ' + mistake['context']['text'])

        if no_grammar_errors:
            html += '<p>Great! There are no grammar errors.</p>'

        # Spelling
        spell_check = grammar_check['spell_check']
        html += '<h3>Spelling</h3>'

        if len(spell_check) > 0:
            html += self._render_html_list(spell_check, lambda mistake: '"' + mistake['word'] + '" can be corrected as ' + ', '.join(mistake['corrections']))
        else:
            html += '<p>Good, there are no spelling mistakes.</p>'

        # Citation
        citation_check = data['citation_check']
        html += '<h3>Citation</h3>'

        if citation_check['result']:
            html += '<p>Correctly cited the text.</p>'
        else:
            html += '<p>The citation cannot be found or wrong. Here are some examples of possible citations:</p>'
            html += self._render_html_list(citation_check['possible_citations'])

        # Style
        style_check = data['academic_style_check']
        no_style_errors = True
        html += '<h3>Style</h3>'

        if len(style_check['contractions']) > 0:
            no_style_errors = False
            html += '<p>The following contraction forms have been found:</p>'
            html += self._render_html_list(style_check['contractions'])

        if len(style_check['phrasal_verbs']) > 0:
            no_style_errors = False
            html += '<p>The following phrasal verbs have been found:</p>'
            html += self._render_html_list(style_check['phrasal_verbs'])

        if len(style_check['general_informalities']) > 0:
            no_style_errors = False
            html += '<p>The following general informalities have been found:</p>'
            html += self._render_html_list(style_check['general_informalities'])

        if no_style_errors:
            html += 'Great! There are no style warnings.'

        return html

    def run(self, data):
        """Runs the interpreter.

        Args:
            data (dict): The raw data from the checker

        Returns:
            dict: The interpreted data to process in the templates.
        """

        comments = '<h2>Submission</h2>'
        comments += data['text'] + '<br /><br />'
        comments += '<h2>Feedback</h2>'

        if self._is_in_band_4(data):
            data['score'] = 0
            comments += '<p>The submission requires tutor guidance.</p>'
        elif self._is_in_band_3(data):
            data['score'] = 0.6
            comments += '<p>You did good; however check the feedback for more details.</p>'
        elif self._is_in_band_2(data):
            data['score'] = 0.8
            comments += '<p>Great job! You only made few mistakes.</p>'
        elif self._is_in_band_1(data):
            data['score'] = 1
            comments += '<p>Great job! Your paraphrase is consistent and accurate.</p>'

        comments += self._to_html(data)
        data['comments'] = comments

        return data
