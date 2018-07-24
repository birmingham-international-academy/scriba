"""Provides citation checkers using different referencing formats."""

import re

from lti_app.core.exceptions import BadlyFormattedCitationException


class Checker:
    """Implements the default Harvard citation checking.

    Args:
        text (string): The text submitted by the student.
        reference (string): The reference to cite in the text.
    """

    def __init__(self, text, reference):
        self.text = text
        self.reference = reference

    def run(self):
        """Run the checker.

        Returns:
            dict: A dictionary containing the result, correct citations,
            and the extracted authors
        """

        m = re.match(
            r'^(?P<authors>(?:(?:\w+,\s?(?:\w\.)+)(?:,\s?|\sand\s|,\s?and\s)?)+)\s?'
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
            for author in re.split(r',|\sand\s', data['authors'].strip())
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

        possible_citations = [
            lastnames_citation + ' (' + year + ')',
            '(' + lastnames_citation + ', ' + year + ')',
            '(' + lastnames_citation + ' ' + year + ')'
        ]

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
