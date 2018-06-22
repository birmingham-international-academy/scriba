import os
import sys
import requests
import zipfile

date = '2018-02-27'
base = 'https://nlp.stanford.edu/software/stanford-parser-full-'
resource_url = base + date + '.zip'
current_filename = os.path.dirname(os.path.realpath(__file__))
filename = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__))
    + '/../lti/core/data/stanford-parser.zip'
)

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

datapath = os.path.abspath(current_filename + '/../lti/core/data')
os.rename(
    os.path.join(datapath, 'stanford-parser-full-' + date),
    os.path.join(datapath, 'stanford-parser')
)
os.remove(filename)

print('> Stanford Parser successfully installed!')
