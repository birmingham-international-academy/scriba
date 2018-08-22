import requests
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from lti_app import strings


@require_POST
def index(request):
    data = request.POST

    max_points = data.get('custom_canvas_assignment_points_possible')
    request.session[strings.course_id] = data.get('custom_canvas_course_id')
    request.session[strings.assignment_id] = data.get('custom_canvas_assignment_id')
    request.session[strings.assignment_type] = 'D' if int(max_points) == 0 else 'G'

    return redirect('/assignments')
