import glob
import os
import sys

from .utils import download, extract, get_data_directory


data_dir = get_data_directory()
stanford_corenlp_directory = os.path.join(data_dir, 'stanford-corenlp')
base = 'https://nlp.stanford.edu/software'
corenlp_filename = 'stanford-corenlp-full-2018-02-27.zip'
srparser_filename = 'stanford-srparser-2014-10-23-models.jar'
corenlp_url = '{0}/{1}'.format(base, corenlp_filename)
srparser_url = '{0}/{1}'.format(base, srparser_filename)


# Download Stanford CoreNLP
# =============================================
def download_stanford_corenlp():
    zip_filename = os.path.join(data_dir, 'stanford-corenlp.zip')

    with open(zip_filename, 'wb') as f:
        print('> Downloading Stanford CoreNLP ...')
        download(corenlp_url, f)

    print('\n> Extracting contents...')
    extract(zip_filename, data_dir)

    matches = glob.glob(os.path.join(data_dir, 'stanford-corenlp-full-*'))

    for filename in matches:
        os.rename(
            os.path.join(data_dir, filename),
            os.path.join(data_dir, 'stanford-corenlp')
        )
    os.remove(zip_filename)

    if not os.path.isdir(stanford_corenlp_directory):
        print('ERROR: Stanford CoreNLP has not been installed correctly!')
        sys.exit(1)


# Download Shift-Reduce Parser
# =============================================
def download_srparser():
    jar_filename = os.path.join(stanford_corenlp_directory, srparser_filename)

    with open(jar_filename, 'wb') as f:
        print('> Downloading Stanford Shift-Reduce Parser...')
        download(srparser_url, f)


if os.path.isdir(stanford_corenlp_directory):
    print('INFO: Already installed Stanford CoreNLP.')
else:
    download_stanford_corenlp()

if os.path.isfile(os.path.join(stanford_corenlp_directory, srparser_filename)):
    print('INFO: Already installed Stanford Shift-Reduce Parser.')
else:
    download_srparser()

print('\nSuccessfully installed Stanford CoreNLP!')
