from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from . import middleware
from lti.core.api import CanvasApiClient
import requests


@require_POST
def index(request):
    canvas_client = CanvasApiClient()
    data = request.POST

    if request.session.get('lis_result_sourcedid') is None:
        pass  # error

    response = canvas_client.get_assignment(
        data.get('custom_canvas_course_id'),
        data.get('custom_canvas_assignment_id')
    )

    if response.status_code != 200:
        # TODO: fix this
        request.session['session_flash'] = {
            'type': 'error',
            'message': 'Could not load the assignment correctly.\
                        Please refresh the page.'
        }
    else:
        assm = response.json()

        request.session['assignment_description'] = assm.get('description')

        pilot = int(assm.get('points_possible')) == 0
        request.session['assignment_type'] = 'pilot' if pilot else 'graded'

        request.session['assignment_points_possible'] =\
            float(assm.get('points_possible'))

    return redirect('/assignments')
