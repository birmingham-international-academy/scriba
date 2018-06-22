import os
import fnmatch
import string
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer


def get_current_dir(current_file):
    return os.path.dirname(os.path.realpath(current_file))


def find_file(pattern, path, first=False):
    result = []

    for root, _, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))

    return result[0] if first else result


def remove_punctuation(s):
    return ''.join(c for c in s if c not in '!?.,;:')


def is_punctuation(s):
    return s in string.punctuation


def dice_coefficient(a, b):
    if not len(a) or not len(b):
        return 0.0

    if a == b:
        return 1.0

    if len(a) == 1 or len(b) == 1:
        return 0.0

    a_bigram_list = [a[i:i+2] for i in range(len(a)-1)]
    b_bigram_list = [b[i:i+2] for i in range(len(b)-1)]

    a_bigram_list.sort()
    b_bigram_list.sort()

    lena = len(a_bigram_list)
    lenb = len(b_bigram_list)

    matches = i = j = 0

    while (i < lena and j < lenb):
        if a_bigram_list[i] == b_bigram_list[j]:
            matches += 2
            i += 1
            j += 1
        elif a_bigram_list[i] < b_bigram_list[j]:
            i += 1
        else:
            j += 1

    score = float(matches) / float(lena + lenb)

    return score


def tok_and_lem(text):
    lemmatizer = WordNetLemmatizer()
    text_tokens = word_tokenize(text)
    return [lemmatizer.lemmatize(token) for token in text_tokens]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
