from . import api

class CitationChecker:
    def __init__(self):
        self.freecite_client = api.FreeCiteApiClient()

    def run(self, text, citation_string):
        data = self.freecite_client.parse(citation_string)
        authors = [author.split(' ')[-1] for author in data['authors']]
        year = data['year']

        lastnames_citation = authors[0]

        if len(authors) >= 4:
            lastnames_citation += ' et al.'
        else:
            for index, author in enumerate(authors):
                if index == 0:
                    continue

                lastnames_citation += author

                if index == len(authors) - 2:
                    lastnames_citation += ' and '
                elif index != len(authors) - 1:
                    lastnames_citation += ', '

        possible_citations = [
            lastnames_citation + ' (' + year  + ')',
            '(' + lastnames_citation + ', ' + year + ')',
            '(' + lastnames_citation + ' ' + year + ')'
        ]

        result = False

        for cit in possible_citations:
            if cit in text:
                result = True
                break

        return {
            'result': result,
            'possible_citations': possible_citations
        }

