import os

from .utils import download, extract, get_data_directory


resource_url = 'https://www.languagetool.org/download/LanguageTool-stable.zip'
data_dir = get_data_directory()
filename = os.path.join(data_dir, 'languagetool.zip')

with open(filename, 'wb') as f:
    print('> Downloading languagetool.zip')
    download(resource_url, f)

print('\n> Extracting contents to languagetool')
extract(filename, os.path.dirname(filename))

# LanguageTool-*
# http://languagetool.org/download/ngram-data/ngrams-en-20150817.zip

os.rename(
    os.path.join(data_dir, ''),
    os.path.join(data_dir, 'languagetool')
)
os.remove(filename)

print('> LanguageTool successfully installed!')
