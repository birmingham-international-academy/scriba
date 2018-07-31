"""Collection of citation checkers using different referencing formats."""

import re

from lti_app.core.exceptions import BadlyFormattedCitationException


class Checker:
    """The default Harvard citation checking.

    Args:
        text (string): The text submitted by the student.
        reference (string): The reference to cite in the text.
    """

    def __init__(self, text, reference):
        self.text = text
        self.reference = reference

    def _get_citation_patterns(self, authors, year):
        return [
            authors + ' (' + year + ')',
            '(' + authors + ', ' + year + ')',
            '(' + authors + ' ' + year + ')'
        ]

    def run(self):
        """Run the checker.

        Returns:
            dict: A dictionary containing the result, correct citations,
            and the extracted authors
        """

        m = re.match(
            r'^(?P<authors>(?:(?:\w+,\s?(?:\w\.)+)(?:,\s?|\sand\s|,\s?and\s|\s&\s|,\s?&\s)?)+)\s?'
            r'\((?P<year>\d{4})\)\s'
            r'(?:\"|\')?(?P<title>[^\"\'\.]+)(?:\"|\')?\.?'
            r'.*$',
            self.reference
        )

        if m is None:
            raise BadlyFormattedCitationException()

        data = m.groupdict()

        year = data['year']
        authors = [
            author.strip()
            for author in re.split(r',|\sand\s|\s&\s', data['authors'].strip())
        ]
        authors = authors[::2]

        lastnames_citation = ''

        if len(authors) >= 4:
            lastnames_citation += authors[0] + ' et al.'
        else:
            for index, author in enumerate(authors):
                lastnames_citation += author

                if index == len(authors) - 2:
                    lastnames_citation += ' and '
                elif index != len(authors) - 1:
                    lastnames_citation += ', '

        possible_citations = self._get_citation_patterns(
            lastnames_citation,
            year
        )

        if ' and ' in lastnames_citation:
            lastnames_citation_ampersand = lastnames_citation.replace(
                ' and ',
                ' & '
            )

            possible_citations += self._get_citation_patterns(
                lastnames_citation_ampersand,
                year
            )

        result = False

        text = self.text.lower()
        possible_citations_lower = [cit.lower() for cit in possible_citations]

        for cit in possible_citations_lower:
            if cit in text:
                result = True
                break

        # Check if citation is after a full stop.
        last_sentence = text.split('.')[-1].strip()
        citation_after_full_stop = last_sentence in possible_citations_lower

        return {
            'result': result,
            'possible_citations': possible_citations,
            'citation_after_full_stop': citation_after_full_stop,
            'authors': authors,
            'year': year
        }
