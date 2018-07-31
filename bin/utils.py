import os
import sys

import requests
import zipfile


def download(url, fp):
    response = requests.get(url, stream=True)
    total_length = response.headers.get('content-length')

    if total_length is None:
        fp.write(response.content)
    else:
        dl = 0
        total_length = int(total_length)
        for data in response.iter_content(chunk_size=4096):
            dl += len(data)
            fp.write(data)
            done = int(50 * dl / total_length)
            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
            sys.stdout.flush()


def extract(source_path, target_path):
    zp = zipfile.ZipFile(source_path)
    zp.extractall(target_path)
    zp.close()


def get(url):
    response = requests.get(url)
    return response.text


def get_data_directory():
    current_filename = os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(os.path.join(
        current_filename,
        '../'
        'lti_app',
        'core',
        'data'
    ))
