"""Database models for the LTI app."""


from django.db import models


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
    max_attempts = models.IntegerField(null=True)
    show_excerpt = models.BooleanField(default=True)
    citation_check = models.BooleanField(default=True)
    grammar_check = models.BooleanField(default=True)
    plagiarism_check = models.BooleanField(default=True)
    academic_style_check = models.BooleanField(default=True)
    semantics_check = models.IntegerField(default=1)

    def __str__(self):
        return self.course_id + ':' + self.assignment_id
