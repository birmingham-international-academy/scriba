"""Provides base repository classes.

Todo:
- Add validation
"""


class CrudRepository:
    def __init__(self, model):
        self.model = model

    def get_all(self):
        return self.model.objects.all()

    def get_by_id(self, id):
        return self.model.objects.get(pk=id)

    def get_by(self, fields):
        return self.model.objects.all().filter(**fields)

    def create(self, fields):
        obj = self.model(**fields)
        obj.save()
