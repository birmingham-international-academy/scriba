"""
{
    'academic_style_check': {
        'contractions': [],
        'phrasal_verbs': [],
        'general_informalities': []
    },
    'semantics_check': None,
    'grammar_check': {
        'languagetool_check': [],
        'malformed_sentences': [],
        'spell_check': [],
        'run_ons': [],
        'transitive_verbs_without_object': [],
        'sentence_fragments': [],
        'noun_verb_disagreements': []
    },
    'plagiarsim_check': {
        'four_words': [],
        'three_words': [],
        'six_words': [],
        'five_words': []
    },
    'citation_check': {
        'possible_citations': ['Candy (2017)', '(Candy, 2017)', '(Candy 2017)'], 'result': False
    }
}
"""

# TODO: STORE SETTINGS

class FeedbackInterpreter:
    def run(self, data):
        # Grammar status
        gc = data['grammar_check']
        data['grammar_status'] = len(gc['malformed_sentences']) == 0\
                            and len(gc['languagetool_check']) == 0\
                            and len(gc['run_ons']) == 0\
                            and len(gc['transitive_verbs_without_object']) == 0\
                            and len(gc['sentence_fragments']) == 0\
                            and len(gc['noun_verb_disagreements']) == 0

        # Spelling status
        data['spelling_status'] = len(gc['spell_check']) == 0

        # Academic style status
        asc = data['academic_style_check']
        data['academic_style_status'] = len(asc['contractions']) == 0\
                                    and len(asc['phrasal_verbs']) < 3\
                                    and len(asc['general_informalities']) == 0

        # Paraphrase status
        pc = data['plagiarsim_check']
        sc = data['semantics_check']
        data['paraphrase_status'] = len(pc['three_words']) < 2\
                                and len(pc['four_words']) == 0\
                                and len(pc['five_words']) == 0\
                                and len(pc['six_words']) == 0

        return data

class GradeInterpreter:
    def run(self, data):
        data['score'] = 0.87
        data['comments'] = 'You did good man!\nKeep up the great work!'
        return data
