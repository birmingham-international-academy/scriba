import hashlib
from functools import wraps

from django.core.cache import cache

from .exceptions import CachingException


def get_hash(text):
    hash_object = hashlib.sha256(text.encode('utf-8'))
    return hash_object.hexdigest()


def from_cache(text):
    digest = get_hash(text)
    return cache.get(digest)


def save_cache(text, data):
    digest = get_hash(text)
    cache.set(digest, data, None)


def caching(name):
    def wrap(func):
        @wraps(func)
        def wrapped_f(self, *args, **kwargs):
            if not hasattr(self, 'cache'):
                raise CachingException.not_cacheable()

            ext_key = name

            # Get name if given as a class path
            # ---------------------------------------------
            if type(ext_key) is list:
                if len(ext_key) == 0:
                    raise CachingException.generic()

                attr_key, rest = ext_key[0], ext_key[1:]

                if not hasattr(self, attr_key):
                    raise CachingException.invalid_key()

                attr = getattr(self, attr_key)

                for key in rest:
                    if attr is None or type(attr) is not dict:
                        raise CachingException.invalid_key()

                    attr = attr.get(key)

                ext_key = attr

            # Get result from cache (if stored)
            # ---------------------------------------------
            key = self.cache.base_key + str(ext_key)

            result = from_cache(key)

            if self.cache.enabled and result is not None:
                return result

            # Compute result without cache
            # ---------------------------------------------
            result = func(self, *args, **kwargs)

            # Save result in cache if enabled
            # ---------------------------------------------
            if self.cache.enabled:
                save_cache(key, result)

            return result
        return wrapped_f
    return wrap


class Cache:
    def __init__(self, enabled=False, base_key=None):
        self.enabled = enabled
        self.base_key = base_key

    def get(self, key):
        key = self.base_key + key
        return from_cache(key)

    def put(self, key, data):
        key = self.base_key + key
        save_cache(key, data)
