from .citation_checker import CitationChecker
from .academic_style_checker import AcademicStyleChecker
from .semantics_checker import SemanticsChecker
from .grammar_checker import GrammarChecker

class Checker:
    def __init__(self):
        self.citation_checker = CitationChecker()
        self.academic_style_checker = AcademicStyleChecker()
        self.semantics_checker = SemanticsChecker()
        self.grammar_checker = GrammarChecker()

    def run(self, text, excerpt, reference):
        citation_check = self.citation_checker.run(text, reference)
        academic_style_check = self.academic_style_checker.run(text)
        semantics_check = self.semantics_checker.run(text, excerpt)
        grammar_check = self.grammar_checker.run(text)

        return {
            'citation_check': citation_check,
            'academic_style_check': academic_style_check,
            'semantics_check': semantics_check,
            'grammar_check': grammar_check
        }
