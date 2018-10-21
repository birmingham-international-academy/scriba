"""Provides service classes for the assignment views."""

from html import parser

from django.conf import settings
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
        return self.repository.create(fields)

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
            attempts,
            outcome_service_url,
            result_sourcedid,
            text):
        # 1. Retrieve the assignment details
        assignment = self.repository.get_by({
            'course_id': course_id,
            'assignment_id': assignment_id
        }).first()

        # 2. Create the interpreter for the raw data
        feedback_interpreter = interpreters.FeedbackInterpreter(assignment.semantics_check)
        grade_interpreter = interpreters.GradeInterpreter(assignment_type, assignment.semantics_check)

        # 3. Select the checks to run
        checks = {
            'citation': assignment.citation_check,
            'grammar': assignment.grammar_check,
            'plagiarism': assignment.plagiarism_check,
            'academic_style': assignment.academic_style_check,
            'semantics': assignment.semantics_check
        }

        # 4. Run the analysis
        checker = checkers.DefaultChecker(
            text,
            assignment.excerpt,
            assignment.supporting_excerpts,
            assignment.reference,
            checks
        )
        data = checker.run()
        data['assignment'] = assignment
        data['is_last_attempt'] = attempts == assignment.max_attempts - 1
        data['text'] = text

        # 5. Run the interpreter(s)
        feedback_interpreter.run(data)

        grade_interpreter.run(data)

        # 6. Send the grade
        self._send_grade(outcome_service_url, result_sourcedid, data)

        return data
