"""Provides service classes for the assignment views."""

from django.conf import settings
from html import parser
from lti import tool_provider

from lti_app.core import checkers, interpreters
from lti_app.assignments import repositories


class AssignmentService:
    def __init__(self):
        self.repository = repositories.AssignmentRepository()

    def _send_grade(self, outcome_service_url, result_sourcedid, data):
        tp = tool_provider.ToolProvider(
            consumer_key=settings.CANVAS['CONSUMER_KEY'],
            consumer_secret=settings.CANVAS['SHARED_SECRET'],
            params={
                'lis_outcome_service_url': outcome_service_url,
                'lis_result_sourcedid': result_sourcedid
            }
        )

        tp.post_replace_result(
            data.get('score'),
            result_data={'text': data.get('comments')}
        )

    def create(self, fields):
        self.repository.create(fields)

    def update(self, model_id, fields):
        self.repository.update(model_id, fields)

    def get_by_course_assignment_tuple(self, course_id, assignment_id):
        return self.repository.get_by({
            'course_id': course_id,
            'assignment_id': assignment_id
        })

    def run_analysis(
            self,
            course_id,
            assignment_id,
            assignment_type,
            outcome_service_url,
            result_sourcedid,
            text):
        # 1. Retrieve the assignment details
        assignment = self.repository.get_by({
            'course_id': course_id,
            'assignment_id': assignment_id
        }).first()

        # 2. Create the interpreter for the raw data
        interpreter = (
            interpreters.FeedbackInterpreter()
            if assignment_type == 'D'
            else interpreters.GradeInterpreter(assignment.max_points)
        )

        # 3. Run the analysis
        checker = checkers.DefaultChecker(
            text,
            assignment.excerpt,
            assignment.reference
        )
        data = checker.run()
        data['text'] = text

        # 4. Run the interpreter
        data = interpreter.run(data)

        # 5. (Optional) Send the grade
        if assignment_type != 'D':
            self._send_grade(outcome_service_url, result_sourcedid, data)

        return data
