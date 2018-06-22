# scriba

> A Canvas LTI for automated paraphrase analysis: a project part of the Birmingham International Academy (University of Birmingham, UK).

## Development setup

Scriba is compatible with Python 3.5.2.

First of all install the dependencies using: `pip -r requirements.txt`.

### 1. Environment settings

Create a `.env` file resembling the `.env.example` file in the same directory.

Then set the keys appropriately:
- `SECRET_KEY`: Django secret key.
- `CANVAS_CONSUMER_KEY`: Canvas consumer key for LTI communication. This can be generated as a 256-bit key.
- `CANVAS_SHARED_SECRET`: Canvas consumer/shared secret for LTI communication. This can be generated as a 256-bit key.
- `CANVAS_PERSONAL_ACCESS_TOKEN`: Canvas personal access token for testing purposes.
- `CANVAS_DEVELOPER_KEY`: Canvas API key.
- `DANDELION_API_KEY`: Text semantic similarity service offered by Dandelion (deprecated).

### 2. NLTK (Natural Language Toolkit) package

After installing the required packages, we need to download corpora that is used by NLTK.

- Run the Python interpreter: `$ python`
- Run the following:

```
>>> import nltk
>>> nltk.download()
```

- Press `d`
- Then enter `popular` to download the 'popular' packages of NLTK

### 3. NLTK interface to the Stanford Parser

The Stanford Parser is a probabilistic parser written in Java. NLTK provides a Python interface to it;
so let's setup the Java environment:

- `sudo apt-get install default-jre`
- `sudo apt-get install default-jdk`

Then run `python scripts/stanford_parser.py` to download and extract the Stanford parser.

### 4. SpaCy package

Run the following command to download the 'en' model for SpaCy: `python -m spacy download en`
