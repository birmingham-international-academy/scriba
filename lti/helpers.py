import os, fnmatch

def get_current_dir(current_file):
    return os.path.dirname(os.path.realpath(current_file))

def find_file(pattern, path):
    result = []

    for root, _, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))

    return result
