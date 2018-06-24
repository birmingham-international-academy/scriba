"""Middleware for launch views."""

from django.conf import settings
from lti_app.launch import exceptions
from lti_app.core import services
from lti.contrib import django as lti_django


class ValidLaunchMiddleware:
    """A middleware to check if a launch request is a valid one."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        outcome_url = 'lis_outcome_service_url'
        result_sourcedid = 'lis_result_sourcedid'
        method = request.method.lower()

        # If it's not a launch request just skip the validation
        if not method == 'post' or not request.POST.get(outcome_url):
            return self.get_response(request)

        tool_provider = lti_django.DjangoToolProvider.from_django_request(
            request=request
        )

        validator = services.ScribaRequestValidator()

        ok = tool_provider.is_valid_request(validator)

        if not ok:
            raise exceptions.InvalidLaunchError()

        data = request.POST

        # Store relevant data in session
        if data.get(outcome_url) and data.get(result_sourcedid):
            request.session[outcome_url] = data.get(outcome_url)
            request.session[result_sourcedid] = data.get(result_sourcedid)

        request.session['is_instructor'] = tool_provider.is_instructor()

        return self.get_response(request)
