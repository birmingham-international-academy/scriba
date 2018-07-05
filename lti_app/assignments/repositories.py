"""Provides repositories that communicate to the DB."""

from lti_app.repositories import CrudRepository
from lti_app.models import Assignment


class AssignmentRepository(CrudRepository):
    def __init__(self):
        CrudRepository.__init__(self, Assignment)
