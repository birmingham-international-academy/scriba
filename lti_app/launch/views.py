from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from lti_app.core.api import CanvasApiClient
import requests


@require_POST
def index(request):
    data = request.POST

    # if request.session.get('lis_result_sourcedid') is None:
    #        print('Not good')

    max_points = data.get('custom_canvas_assignment_points_possible')

    request.session['course_id'] = data.get('custom_canvas_course_id')
    request.session['assignment_id'] = data.get('custom_canvas_assignment_id')
    request.session['assignment_type'] = 'D' if int(max_points) == 0 else 'G'
    request.session['assignment_max_points'] = max_points

    return redirect('/assignments')
