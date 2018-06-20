import random, os, sys

lti_helpers = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..'))
sys.path.insert(0, lti_helpers)

import helpers
from nltk.corpus import masc_tagged
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.parse.stanford import StanfordParser, Tree

POS_TYPES = {
    'NOUN': ['NN', 'NNS', 'NNP', 'NNPS'],
    'VERB': ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD'],
    'DETERMINER': ['DT', 'WDT', 'PDT'],
    'ADJECTIVE': ['JJ', 'JJR', 'JJS'],
    'ADVERB': ['RB', 'RBR', 'RBS', 'WRB'],
    'PREPOSITION': ['IN', 'TO'],
    'PRONOUN': ['PRP', 'PRP$', 'WP', 'WP$'],
    'PUNCTUATION': ['.', ':', ';', ','],
    'OTHER': [],
}

ERROR_TYPES = [
    {
        'name': 'insertion',
        'supported_pos': list(POS_TYPES.keys()),
        'weight': 1
    },

    {
        'name': 'omission',
        'supported_pos': list(POS_TYPES.keys()),
        'weight': 1
    },

    {
        'name': 'displacement',
        'supported_pos': list(POS_TYPES.keys()),
        'weight': 1
    },

    {
        'name': 'number',
        'supported_pos': ['NOUN', 'DETERMINER', 'PRONOUN'],
        'weight': 1
    },

    {
        'name': 'tense',
        'supported_pos': ['VERB'],
        'weight': 1
    },

    {
        'name': 'objectivity',
        'supported_pos': ['PRONOUN'],
        'weight': 1
    },

    {
        'name': 'case',
        'supported_pos': ['NOUN'],
        'weight': 1
    }
]

class Utils:
    @staticmethod
    def intersect(s1, s2):
        return list(filter(lambda x: x in s1, s2))

class ErrorSentence:
    def __init__(self, original_form, error_form, error_types):
        self.original_form = original_form
        self.error_form = error_form
        self.error_types = error_types

class MarkedTagging:
    def __init__(self, index, token, tag):
        self.original_index = index
        self.token = token
        self.tag = tag
        self.used = False

class Corpora:
    def __init__(self):
        self.tagged_correct_sentences = masc_tagged.tagged_sents('written/blog-varsity-athletics.txt')
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

        stanford_parser_directory = os.path.join(self.data_dir, 'stanford-parser')
        parser_jar_filename = os.path.join(stanford_parser_directory, 'stanford-parser.jar')
        models_jar_filename = helpers.find_file('stanford-parser-*-models.jar', stanford_parser_directory)[0]
        self.stanford_parser = StanfordParser(parser_jar_filename, models_jar_filename, corenlp_options='-printPCFGkBest 2')

    def generate_incorrect_sentences_from_fce(self):
        input_corpus_filename = os.path.join(self.data_dir, 'fce-corpus-in')
        output_corpus_filename = os.path.join(self.data_dir, 'fce-corpus')
        os.remove(output_corpus_filename)
        file_in = open(input_corpus_filename)
        file_out = open(output_corpus_filename, 'a')

        sentences = []
        tokens = ''

        for line in file_in:
            if len(sentences) == 100:
                file_out.writelines(sentences)
                sentences = []

            if line == '\n':
                sentences.append(tokens.strip() + '\n')
                tokens = ''
            else:
                word = line.split('\t')[0]

                if "'" in word or word in ['.', ',', '?', '!', ':', ';', '...', '-']:
                    tokens += word
                else:
                    tokens += (' ' + word)

        file_in.close()
        file_out.close()

    def generate_data_features(self):
        corpus = PlaintextCorpusReader(self.data_dir, 'fce-corpus')

        for index, sentence in enumerate([' '.join(words) for words in corpus.sents()]):
            if index >= 5:
                break
            print(self.stanford_parser.raw_parse(sentence))
            #print(self.stanford_parser. sentence)

    def generate_error_sentences(self, error_types, error_quantity, exact_number_of_errors_only):
        incorrect_sentences = []

        for tagged_correct_tokens in self.tagged_correct_sentences:
            n = error_quantity
            errors_indexes = dict() #new HashMap<Integer, ErrorType>(o.errorsPerSentence)
            error_tags = [MarkedTagging(index, token[0], token[1]) for index, token in enumerate(tagged_correct_tokens)]

            while n > 0:
                valid_error_types = []
                tags = [mt.tag for mt in error_tags if not mt.used]

                if len(tags) == 0:
                    break

                total_weight = 0

                for et in error_types:
                    if et['name'] in valid_error_types:
                        continue

                    for pt in et['supported_pos']:
                        if pt == 'OTHER' or len(Utils.intersect(tags, POS_TYPES[pt])) > 0:
                            valid_error_types.append(et['name'])
                            total_weight += et['weight']
                            break

                # Sort error types by weight
                error_types = sorted(error_types, key=lambda k: k['weight'], reverse=True)

                error_type = None
                r = random.uniform(0, 1)
                for e in error_types:
                    if e['name'] not in valid_error_types:
                        continue

                    wr = e['weight'] / total_weight

                    if (r < wr):
                        error_type = e
                        break

                    r -= wr

                if error_type is None:
                    continue


                # Gather all tokens that apply to this error_type
                indexes = []

                for index, et in enumerate(error_tags):
                    if et.used:
                        continue

                    for pt in error_type['supported_pos']:
                        if pt == 'OTHER' or et.tag in POS_TYPES[pt]:
                            indexes.append(index)

                # Pick a random tag
                ir = random.randint(0, len(indexes) - 1)
                i = indexes[ir]
                error_tag = error_tags[i]

                # Apply error
                if error_type['name'] == 'insertion':
                    i_insert = random.randint(0, len(error_tags) - 1)
                    error = MarkedTagging(i_insert, error_tag.token, error_tag.tag)
                    error.used = True
                    error_tags.insert(i_insert, error)
                    error_tag.used = True
                elif error_type['name'] == 'omission':
                    error_tags.pop(i)
                    error_tag.used = True
                elif error_type['name'] == 'displacement':
                    pass

                if not error_tag.used:
                    error_tag.used = True
                    n += 1
                    continue
                else:
                    errors_indexes[str(error_tag.original_index)] = error_type
                    n -= 1

            # Rebuild a sentence from the error tokens
            error_words = ''

            for mt in error_tags:
                error_words += (mt.token + ' ')

            # TODO: check
            if len(errors_indexes) > 0 and (not exact_number_of_errors_only or len(errors_indexes) == error_quantity):
                incorrect_sentences.append(ErrorSentence(tagged_correct_tokens, error_words.strip(), errors_indexes))

        return incorrect_sentences



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please supply an action: GEN | FT')
        sys.exit(1)

    corpus = Corpora()

    if sys.argv[1] == 'GEN':
        corpus.generate_incorrect_sentences_from_fce()
    elif sys.argv[1] == 'FT':
        corpus.generate_data_features()

    #incorrect_sentences = corpus.generate_error_sentences(ERROR_TYPES, 3, False)

    #for incorrect_sentence in incorrect_sentences:
    #    print(incorrect_sentence.error_form)
