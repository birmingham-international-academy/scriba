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

    def __str__(self):
        return self.course_id + ':' + self.assignment_id
