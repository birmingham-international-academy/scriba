# TODO: STORE SETTINGS


class FeedbackInterpreter:
    def run(self, data):
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
    def __init__(self, points_possible):
        self.points_possible = points_possible

    def _points_to_decimal_score(self, points):
        return points / self.points_possible

    def _decimal_to_points_score(self, decimal):
        return decimal * self.points_possible

    def run(self, data):
        data['score'] = 0.87
        data['comments'] = 'You did good man!\nKeep up the great work!'
        return data
