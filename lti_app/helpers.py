"""Provides general utilities."""

import fnmatch
import string
import os
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer


def contains_list(list1, list2):
    return all(elem in list1 for elem in list2)


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

    result = []

    for root, _, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))

    return result[0] if first else result


def remove_punctuation(s):
    """Remove punctuation from an input string.

    Args:
        s (str): The string to remove punctuation from.

    Returns:
        str: The string without punctuation.
    """

    return ''.join(c for c in s if c not in '!?.,;:')


def is_punctuation(s):
    """Checks if the input string is a punctuation character.

    Args:
        s (str): The string.

    Returns:
        bool: Whether the string contains a punctuation character.
    """

    return s in string.punctuation


def tok_and_lem(text):
    """Tokenize and lemmatize an input text.

    Args:
        text (str): The sentence text.

    Returns:
        list: A list of lemmatized tokens from the original text.
    """

    lemmatizer = WordNetLemmatizer()
    text_tokens = word_tokenize(text)
    return [lemmatizer.lemmatize(token) for token in text_tokens]


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