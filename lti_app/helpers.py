"""Provides general utilities."""

import glob
import math
import string
import os

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer


class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


def get_current_dir(current_file):
    """Get the current directory.

    Args:
        current_file (str): The __file__ value from which to get the directory.

    Returns:
        str: The current directory.
    """

    return os.path.dirname(os.path.realpath(current_file))


def find_file(pattern, path, first=False):
    """Finds files given a pattern.

    Args:
        pattern (string): The pattern to search against.
        path (string): The path to apply the pattern to.
        first (bool, optional): Defaults to False. If True get only the
            first match.

    Returns:
        str/list of str: The match(es).
    """

    p = os.path.join(path, pattern)
    result = glob.glob(p)

    return result[0] if first else result


def remove_punctuation(s):
    """Remove punctuation from an input string.

    Args:
        s (str): The string to remove punctuation from.

    Returns:
        str: The string without punctuation.
    """

    return ''.join(c for c in s if c not in '!?.,;:')


def is_number(s):
    """Checks whether a string is a number.

    Args:
        s (str): The string.

    Returns:
        bool: Whether the input string is a number.
    """

    try:
        float(s)
        return True
    except ValueError:
        return False


def find_by(ls, key, value):
    return next((item for item in ls if item[key] == value), None)


def flatten(ls):
    return [item for sublist in ls for item in sublist]
