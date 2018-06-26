from lti import ToolConfig
from django.http import HttpResponse
from django.urls import reverse


def index(request):
    app_title = 'Scriba'
    app_description = 'Provides automated grading for paraphrase assignments.'
    launch_view_name = 'launch_index'
    launch_url = request.build_absolute_uri(reverse(launch_view_name))

    extensions = {
        'canvas.instructure.com': {
            'privacy_level': 'public'
        }
    }

    lti_tool_config = ToolConfig(
        title=app_title,
        launch_url=launch_url,
        secure_launch_url=launch_url,
        description=app_description,
        extensions=extensions
    )

    return HttpResponse(lti_tool_config.to_xml(), content_type='text/xml')
