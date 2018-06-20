from django.conf import settings
from . import exceptions
from lti.core import services


class ValidLaunchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.method.lower() == 'post' or not request.POST.get('lis_outcome_service_url'):
            return self.get_response(request)

        data = {k: v[0] for k, v in dict(request.POST).items()}
        signer = services.HmacSha1Signer()
        generated_signature = signer.build_signature(request, data, settings.CANVAS['SHARED_SECRET'])

        if generated_signature != data.get('oauth_signature'):
            raise exceptions.InvalidLaunchError()

        request.session['roles'] = data.get('roles')

        if data.get('lis_outcome_service_url') and data.get('lis_result_sourcedid'):
            request.session['lis_outcome_service_url'] = data.get('lis_outcome_service_url')
            request.session['lis_result_sourcedid'] = data.get('lis_result_sourcedid')

        return self.get_response(request)
