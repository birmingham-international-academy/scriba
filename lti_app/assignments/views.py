from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rq import Queue

from lti_app.assignments import services
from worker import conn


def _create_or_update_assignment(request):
    service = services.AssignmentService()
    fields = {
        'course_id': request.session.get('course_id'),
        'assignment_id': request.session.get('assignment_id'),
        'assignment_type': request.session.get('assignment_type'),
        'max_points': request.session.get('assignment_max_points'),
        'reference': request.POST.get('reference'),
        'excerpt': request.POST.get('excerpt')
    }

    assignment = service.get_by_course_assignment_tuple(
        fields['course_id'],
        fields['assignment_id']
    ).first()

    if assignment is None:
        service.create(fields)
    else:
        service.update(assignment.id, fields)


def _submit_assignment(request):
    course_id = request.session.get('course_id')
    assignment_id = request.session.get('assignment_id')
    assignment_type = request.session.get('assignment_type')
    outcome_service_url = request.session.get('lis_outcome_service_url')
    result_sourcedid = request.session.get('lis_result_sourcedid')
    text = request.POST.get('text')
    service = services.AssignmentService()
    q = Queue(connection=conn)

    result = q.enqueue(
        service.run_analysis,
        course_id,
        assignment_id,
        outcome_service_url,
        result_sourcedid,
        text
    )

    request.session['job_id'] = result.id

    return JsonResponse({
        'assignment_type': assignment_type
    })


def show(request):
    service = services.AssignmentService()
    course_id = request.session.get('course_id')
    assignment_id = request.session.get('assignment_id')

    assignment = service.get_by_course_assignment_tuple(
        course_id,
        assignment_id
    ).first()

    is_instructor = request.session.get('is_instructor')

    if is_instructor:
        template = 'teacher/index.html'
    else:
        template = 'learner/index.html'

    return render(request, template, {
        'assignment': assignment
    })


def submit(request):
    is_instructor = request.session.get('is_instructor')

    if is_instructor:
        _create_or_update_assignment(request)

        return render(
            request,
            'teacher/assignment-submission-confirmation.html'
        )
    else:
        return _submit_assignment(request)


@require_http_methods(['GET', 'POST'])
def index(request):
    if request.method == 'GET':
        return show(request)
    else:
        return submit(request)
