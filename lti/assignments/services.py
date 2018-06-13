from lti.core.checker import Checker
from lti.core.interpreters import DefaultInterpreter
from html.parser import HTMLParser

class OutcomeService:
    def __init__(self, service_url, source_did):
        self.service_url = service_url
        self.source_did = source_did

class AssignmentDescriptionParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.excerpt = ''
        self.reference = ''
        self.in_excerpt = False
        self.in_reference = False

    def handle_data(self, data):
        _data = data.lower()

        if _data == 'excerpt':
            self.in_excerpt = True
            self.in_reference = False
        elif _data == 'reference':
            self.in_excerpt = False
            self.in_reference = True
        else:
            if self.in_excerpt:
                self.excerpt += data
            elif self.in_reference:
                self.reference += data

class AssignmentService:
    def __init__(self, assm_description, assm_type, service_url, source_did):
        self.type = assm_type
        self.outcome_service = OutcomeService(service_url, source_did) # TODO:
        self._parse_description(assm_description)

    def _parse_description(self, description):
        parser = AssignmentDescriptionParser()
        parser.feed(description)

        self.excerpt = parser.excerpt.strip()
        self.reference = parser.reference.strip()

    def run_analysis(self, text):
        checker = Checker()
        interpreter = DefaultInterpreter()

        data = checker.run(text, self.excerpt, self.reference)
        return interpreter.run(data)

    def send_grade(self):
        pass
