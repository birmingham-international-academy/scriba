import re

class CitationChecker:
    def run(self, text, citation_string):
        m = re.match(
            r'^(?P<authors>(?:(?:\w+,\s?(?:\w\.)+)(?:,\s?|\sand\s)?)+)\s?\((?P<year>\d{4})\)\s(?:\"|\')?(?P<title>[^\"\'\.]+)(?:\"|\')?\.?(?:(?P<edition>\s*\d+.+?)\.)?(?:(?P<publisher>.+?:.+?)\.)?$',
            citation_string
        )

        if m is None:
            pass # raise exception

        data = m.groupdict()

        authors = [author.strip() for index, author in enumerate(re.split(r',|\sand\s', data['authors'].strip())) if index % 2 == 0]
        year = data['year']

        lastnames_citation = ''

        if len(authors) >= 4:
            lastnames_citation += authors[0] + ' et al.'
        else:
            for index, author in enumerate(authors):
                #if index == 0:
                #    continue

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

