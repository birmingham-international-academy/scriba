from .citation_checker import CitationChecker
from .academic_style_checker import AcademicStyleChecker
from .semantics_checker import SemanticsChecker
from .grammar_checker import GrammarChecker
from .plagiarism_checker import PlagiarismChecker


class Checker:
    def __init__(self, text, excerpt, reference):
        self.text = text
        self.excerpt = excerpt
        self.reference = reference

        self.citation_checker = CitationChecker(self.text, self.reference)
        self.academic_style_checker = AcademicStyleChecker(self.text)
        self.semantics_checker = SemanticsChecker(self.text, self.excerpt)
        self.grammar_checker = GrammarChecker(self.text)
        self.plagiarism_checker = PlagiarismChecker(self.text, self.excerpt)

    def run(self):
        citation_check = self.citation_checker.run()
        academic_style_check = self.academic_style_checker.run()
        semantics_check = self.semantics_checker.run()
        grammar_check = self.grammar_checker.run(citation_check.get('authors'))
        plagiarism_check = self.plagiarism_checker.run()

        return {
            'citation_check': citation_check,
            'academic_style_check': academic_style_check,
            'semantics_check': semantics_check,
            'grammar_check': grammar_check,
            'plagiarism_check': plagiarism_check
        }
