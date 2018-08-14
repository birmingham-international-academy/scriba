"""Provides base repository classes."""

from .caching import caching, Cache


class CrudRepository:
    def __init__(self, model):
        self.model = model
        self.cache = Cache(enabled=True, base_key='query_{}_'.format(self.model.__name__))

    @caching('get_all')
    def get_all(self, enable_cache=True):
        return self.model.objects.all()

    @caching('get_by_id_{}', 0)
    def get_by_id(self, id, enable_cache=True):
        return self.model.objects.get(pk=id)

    @caching('get_by_{}', 0)
    def get_by(self, fields, enable_cache=True):
        return self.model.objects.all().filter(**fields)

    def create(self, fields):
        obj = self.model(**fields)
        obj.save()

    def update(self, model_id, fields):
        self.model.objects.filter(id=model_id).update(**fields)
