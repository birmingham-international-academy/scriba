import os

from .utils import download, extract, get_data_directory


date = '2018-02-27'
base = 'https://nlp.stanford.edu/software/stanford-parser-full-'
resource_url = base + date + '.zip'
data_dir = get_data_directory()
filename = os.path.join(data_dir, 'stanford-parser.zip')

with open(filename, 'wb') as f:
    print('> Downloading stanford-parser.zip')
    download(resource_url, f)

print('\n> Extracting contents to stanford-parser')
extract(filename, os.path.dirname(filename))

os.rename(
    os.path.join(data_dir, 'stanford-parser-full-' + date),
    os.path.join(data_dir, 'stanford-parser')
)
os.remove(filename)

print('> Stanford Parser successfully installed!')
