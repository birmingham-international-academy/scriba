from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rq import Queue

from lti_app import strings
from lti_app.assignments import request_forms, services
from worker import conn


def _create_or_update_assignment(request):
    # Prepare fields to submit
    # ---------------------------------------------
    fields = {
        'course_id': request.session.get(strings.course_id),
        'assignment_id': request.session.get(strings.assignment_id),
        'assignment_type': request.session.get(strings.assignment_type)
    }

    req = request_forms.AssignmentRequestForm(request.POST)
    data = req.get_data()
    fields.update(data)

    # Create or update assignment
    # ---------------------------------------------
    service = services.AssignmentService()

    assignment = service.get_by_course_assignment_tuple(
        fields['course_id'],
        fields['assignment_id']
    ).first()

    if assignment is None:
        service.create(fields)
    else:
        service.update(assignment.id, fields)

    return render(
        request,
        'teacher/assignment-submission-confirmation.html'
    )


def _submit_assignment(request):
    course_id = request.session.get(strings.course_id)
    assignment_id = request.session.get(strings.assignment_id)
    assignment_type = request.session.get(strings.assignment_type)
    outcome_service_url = request.session.get(strings.outcome_service_url)
    result_sourcedid = request.session.get(strings.result_sourcedid)
    attempts = request.session.get('{}_{}_attempts'.format(course_id, assignment_id))

    text = request.POST.get('text')
    service = services.AssignmentService()
    q = Queue(connection=conn)

    result = q.enqueue(
        service.run_analysis,
        course_id,
        assignment_id,
        assignment_type,
        attempts,
        outcome_service_url,
        result_sourcedid,
        text
    )

    request.session[strings.job_id] = result.id

    return JsonResponse({
        'assignment_type': assignment_type
    })


def show(request):
    service = services.AssignmentService()
    course_id = request.session.get(strings.course_id)
    assignment_id = request.session.get(strings.assignment_id)

    assignment = service.get_by_course_assignment_tuple(
        course_id,
        assignment_id
    ).first()

    is_instructor = request.session.get(strings.is_instructor)

    if is_instructor:
        template = 'teacher/index.html'
    else:
        template = 'learner/index.html'

    return render(request, template, {
        'assignment': assignment
    })


def submit(request):
    is_instructor = request.session.get(strings.is_instructor)

    if is_instructor:
        return _create_or_update_assignment(request)
    else:
        return _submit_assignment(request)


@require_http_methods(['GET', 'POST'])
def index(request):
    if request.method == 'GET':
        return show(request)
    else:
        return submit(request)
