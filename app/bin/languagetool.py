import glob
import os
from html.parser import HTMLParser

from .utils import download, extract, get, get_data_directory


class NGramResourceFinder(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.ngram_url = None

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == 'href' and 'ngrams-en' in value:
                self.ngram_url = value


data_dir = get_data_directory()
ngram_parser = NGramResourceFinder()

# LanguageTool Codebase
# =============================================

resource_url = 'https://www.languagetool.org/download/LanguageTool-stable.zip'
filename = os.path.join(data_dir, 'languagetool.zip')

print(filename)

with open(filename, 'wb') as f:
    print('> Downloading languagetool.zip')
    download(resource_url, f)

print('\n> Extracting contents to languagetool')
extract(filename, data_dir)

directory_glob = os.path.join(data_dir, 'LanguageTool-*')
for path in glob.glob(directory_glob):
    if os.path.isdir(path):
        os.rename(
            os.path.join(data_dir, path),
            os.path.join(data_dir, 'languagetool')
        )

os.remove(filename)

# LanguageTool ngram data
# =============================================

"""
base_url = 'http://languagetool.org/download/ngram-data/'
filename = os.path.join(data_dir, 'ngram.zip')

with open(filename, 'wb') as f:
    print('> Downloading ngram.zip')

    ngram_parser.feed(get(base_url))
    resource_url = base_url + ngram_parser.ngram_url
    download(resource_url, f)

print('\n> Extracting contents to ngram/en')
ngram_directory = os.path.join(data_dir, 'languagetool', 'ngram', 'en')
if not os.path.exists(ngram_directory):
    os.makedirs(ngram_directory)

extract(filename, ngram_directory)
os.remove(filename)

print('> LanguageTool successfully installed!')
"""
