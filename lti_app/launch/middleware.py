from django.conf import settings
from .exceptions import InvalidLaunchError
from lti_app.core.services import ScribaRequestValidator
from lti.contrib.django import DjangoToolProvider


class ValidLaunchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        outcome_url = 'lis_outcome_service_url'
        result_sourcedid = 'lis_result_sourcedid'
        method = request.method.lower()

        if not method == 'post' or not request.POST.get(outcome_url):
            return self.get_response(request)

        tool_provider = DjangoToolProvider.from_django_request(request=request)

        validator = ScribaRequestValidator()

        ok = tool_provider.is_valid_request(validator)

        if not ok:
            raise InvalidLaunchError()

        data = request.POST

        if data.get(outcome_url) and data.get(result_sourcedid):
            request.session[outcome_url] = data.get(outcome_url)
            request.session[result_sourcedid] = data.get(result_sourcedid)

        request.session['is_instructor'] = tool_provider.is_instructor()

        return self.get_response(request)
