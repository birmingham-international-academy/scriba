# scriba

> A Canvas LTI for automated paraphrase analysis: a project part of the Birmingham International Academy (University of Birmingham, UK).

## Development setup

Install the dependencies using: `pip -r requirements.txt`

### NLTK package

- Run the Python interpreter: `$ python`
- Run the following:

```
>>> import nltk
>>> nltk.download()
```

- Press `d`
- Then enter `popular` to download the 'popular' packages of NLTK

### NLTK interface to the Stanford Parser

First you need set the Java environment for the Java text analysis tools (e.g. Stanford Parser) before you using them in NLTK:

- `sudo apt-get install default-jre`
- `sudo apt-get install default-jdk`

Then run `python scripts/stanford_parser.py` to download and extract the Stanford parser.

### SpaCy package

Run the following command to download the 'en' model for SpaCy: `python -m spacy download en`
