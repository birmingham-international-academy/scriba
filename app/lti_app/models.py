"""Database models for the LTI app."""


from django.db import models

from lti_app import strings


TYPES = (
    ('D', 'Diagnostic'),
    ('G', 'Graded')
)


class Assignment(models.Model):
    course_id = models.CharField(max_length=20)
    assignment_id = models.CharField(max_length=20)
    assignment_type = models.CharField(max_length=1, choices=TYPES)
    reference = models.TextField()
    excerpt = models.TextField()
    supporting_excerpts = models.TextField(null=True)
    model_answers = models.TextField(null=True)

    # General settings
    rubric = models.TextField(null=True)
    graded_confirmation_text = models.TextField(
        default=strings.graded_confirmation_text
    )
    max_attempts = models.IntegerField(null=True)
    show_excerpt = models.BooleanField(default=True)
    show_retry_button = models.BooleanField(default=True)

    # Checks
    citation_check = models.BooleanField(default=True)
    grammar_check = models.BooleanField(default=True)
    plagiarism_check = models.BooleanField(default=True)
    academic_style_check = models.BooleanField(default=True)
    semantics_check = models.IntegerField(default=1)

    def __str__(self):
        return self.course_id + ':' + self.assignment_id
