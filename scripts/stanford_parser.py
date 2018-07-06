import os
import sys
import requests
import zipfile
from django.conf import settings

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "scriba.settings.production"
)

# https://nlp.stanford.edu/software/stanford-parser-full-2018-02-27.zip

date = '2018-02-27'
base = 'https://nlp.stanford.edu/software/stanford-parser-full-'
resource_url = base + date + '.zip'
# current_filename = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(
    settings.BASE_DIR,
    'lti_app',
    'core',
    'data'
)

filename = os.path.join(data_dir, 'stanford-parser.zip')

# filename = os.path.abspath(
#    os.path.dirname(os.path.realpath(__file__))
#    + '/../lti_app/core/data/stanford-parser.zip'
# )

with open(filename, 'wb') as f:
    print('> Downloading stanford-parser.zip')
    response = requests.get(resource_url, stream=True)
    total_length = response.headers.get('content-length')

    if total_length is None:
        f.write(response.content)
    else:
        dl = 0
        total_length = int(total_length)
        for data in response.iter_content(chunk_size=4096):
            dl += len(data)
            f.write(data)
            done = int(50 * dl / total_length)
            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
            sys.stdout.flush()

print('\n> Extracting contents to stanford-parser')
stanford_zip = zipfile.ZipFile(filename)
stanford_zip.extractall(os.path.dirname(filename))
stanford_zip.close()

os.rename(
    os.path.join(data_dir, 'stanford-parser-full-' + date),
    os.path.join(data_dir, 'stanford-parser')
)
# os.remove(filename)

print('> Stanford Parser successfully installed!')
