"""Collection of citation checkers using different referencing formats."""

import re

from lti_app.core.exceptions import CitationException


class Checker:
    """The default citation checking (very lenient).

    Args:
        text (string): The text submitted by the student.
        reference (string): The reference to cite in the text.
    """

    def __init__(self, text, reference):
        self.text = text
        self.reference = reference

    def _get_citation_regexps(self, authors, year):
        authors_regex = r'(?:' + re.escape(authors)

        if ' & ' in authors:
            authors_regex += (
                r'|' + re.escape(authors.replace(' & ', ' and '))
            )
        elif ' and ' in authors:
            authors_regex += (
                r'|' + re.escape(authors.replace(' and ', ' & '))
            )

        authors_regex += r')'

        in_text_regex = (
            authors_regex + r'\'?s?\s*\(\s*' + year + r'\s*\)'
        )

        in_text_separated_regex = (
            r'((?!\()' + authors_regex + r'.*?(?!\(\s*)' + year + r'(?!\s*\)))'
            + r'|(' + year + r'.*?' + authors_regex + r')'
        )

        parenthetical_regex = (
            r'\(' + authors_regex + r'(?:\s*,\s*|\s)' + year + r'\)'
        )

        return {
            'in_text': in_text_regex,
            'in_text_separated': in_text_separated_regex,
            'parenthetical': parenthetical_regex
        }

    def _get_example_citations(self, authors, year):
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

        # Extract reference components
        # ---------------------------------------------
        m = re.match(
            r'^(?P<authors>(?:(?:\w+,\s?(?:\w\.)+)(?:,\s?|\sand\s|,\s?and\s|\s&\s|,\s?&\s)?)+)\s?'
            r'\((?P<year>\d{4})\)\s'
            r'(?:\"|\')?(?P<title>[^\"\'\.]+)(?:\"|\')?\.?'
            r'.*$',
            self.reference
        )

        if m is None:
            raise CitationException.bad_format()

        data = m.groupdict()

        year = data['year']
        authors = [
            author.strip()
            for author in re.split(r',|\sand\s|\s&\s', data['authors'].strip())
        ]
        authors = authors[::2]

        # Build last name part
        # ---------------------------------------------
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

        # Get citation regular expressions and
        # match them against the text
        # ---------------------------------------------
        regexps = self._get_citation_regexps(
            lastnames_citation,
            year
        )

        # Match in text and parenthetical patterns
        in_text_regex = regexps.get('in_text')
        in_text_separated_regex = regexps.get('in_text_separated')
        parenthetical_regex = regexps.get('parenthetical')
        text = self.text.lower()

        in_text_matches = re.findall(in_text_regex, text, re.IGNORECASE)
        in_text_separated_matches = re.findall(in_text_separated_regex, text, re.IGNORECASE)
        parenthetical_matches = re.findall(parenthetical_regex, text, re.IGNORECASE)

        has_in_text_cit = len(in_text_matches) > 0
        has_in_text_separated_cit = len(in_text_separated_matches) > 0
        has_parenthetical_cit = len(parenthetical_matches) > 0
        result = (
            has_in_text_cit
            or has_in_text_separated_cit
            or has_parenthetical_cit
        )

        # Check if citation is after a full stop
        citation_after_full_stop = re.findall(
            r'\.\s?' + parenthetical_regex + r'$',
            text,
            re.IGNORECASE
        )

        # Get examples of citations (for feedback)
        example_citations = self._get_example_citations(lastnames_citation, year)

        return {
            'result': result,
            'in_text': has_in_text_cit,
            'in_text_separated': has_in_text_separated_cit,
            'parenthetical': has_parenthetical_cit,
            'example_citations': example_citations,
            'citation_after_full_stop': citation_after_full_stop,
            'authors': authors,
            'year': year
        }
