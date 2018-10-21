"""Middleware for launch views."""

from django.conf import settings

from lti_app import strings
from lti_app.launch import exceptions
from lti_app.core import services
from lti.contrib import django as lti_django


class ValidLaunchMiddleware:
    """A middleware to check if a launch request is a valid one."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        method = request.method.lower()

        # If it's not a launch request just skip the validation
        if not method == 'post' or not request.POST.get(strings.outcome_service_url):
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
        request.session[strings.is_instructor] = tool_provider.is_instructor()
        request.session[strings.outcome_service_url] = data.get(strings.outcome_service_url)
        request.session[strings.result_sourcedid] = data.get(strings.result_sourcedid)

        return self.get_response(request)
