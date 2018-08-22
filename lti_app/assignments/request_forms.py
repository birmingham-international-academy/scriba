from lti_app.request_forms import BaseRequestForm as BRF


class AssignmentRequestForm(BRF):
    course_id = {'type': str, 'required': True}
    assignment_id = {'type': str, 'required': True}
    assignment_type = {'type': str}
    reference = {'type': str}
    excerpt = {'type': str}
    supporting_excerpts = {'type': str}
    rubric = {'type': str, 'default': None}
    model_answers = {'type': str}
    max_attempts = {'type': int, 'default': 3}
    show_excerpt = {'type': bool, 'get': BRF.get_boolean_from_checkbox}
    citation_check = {'type': bool, 'get': BRF.get_boolean_from_checkbox}
    grammar_check = {'type': bool, 'get': BRF.get_boolean_from_checkbox}
    plagiarism_check = {'type': bool, 'get': BRF.get_boolean_from_checkbox}
    academic_style_check = {'type': bool, 'get': BRF.get_boolean_from_checkbox}
    semantics_check = {'type': int}

    def __init__(self, form_data):
        BRF.__init__(self, form_data)
