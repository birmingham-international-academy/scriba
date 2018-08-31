import django_rq
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from . import request_forms, services
from .exceptions import AssignmentException
from lti_app import strings


@require_http_methods(['GET', 'POST'])
def index(request):
    """Index view. It accepts GET (for listing/showing)
    and POST (for creating/submitting)

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """

    if request.method == 'GET':
        return show(request)
    else:
        return submit(request)


def show(request):
    """The details view for the assignment.
    If the role is a teacher then it will show the assignment settings.
    Otherwise it will show the assignment to complete.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """

    service = services.AssignmentService()
    course_id = request.session.get(strings.course_id)
    assignment_id = request.session.get(strings.assignment_id)
    attempts = request.session.get('{}_{}_attempts'.format(course_id, assignment_id))

    if request.GET.get('reset'):
        request.session[strings.latest_feedback] = None

    latest_feedback = request.session.get(strings.latest_feedback)

    assignment = service.get_by_course_assignment_tuple(
        course_id,
        assignment_id
    ).first()

    context = {'assignment': assignment}

    is_instructor = request.session.get(strings.is_instructor)

    if is_instructor:
        # Instructor
        template = strings.teacher_index
    else:
        # Student
        if latest_feedback is not None and assignment.assignment_type == 'D':
            template = strings.learner_feedback
            latest_feedback.pop('assignment', None)
            context = {
                'assignment': assignment,
                **latest_feedback
            }
        else:
            if (
                attempts is not None
                and attempts >= assignment.max_attempts
            ):
                raise AssignmentException.max_attempts_reached()

            template = strings.learner_index

    return render(request, template, context)


def submit(request):
    """Submit the assignment details either as a student or as a teacher.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """

    is_instructor = request.session.get(strings.is_instructor)

    if is_instructor:
        return _create_or_update_assignment(request)
    else:
        return _submit_assignment(request)


def _create_or_update_assignment(request):
    """Create or update the assignment (restricted to teachers).

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """

    # Prepare fields to submit
    # ---------------------------------------------
    fields = {
        'course_id': request.session.get(strings.course_id),
        'assignment_id': request.session.get(strings.assignment_id),
        'assignment_type': request.session.get(strings.assignment_type),
        **request.POST.dict()
    }

    req = request_forms.AssignmentRequestForm(fields)
    data = req.validate()

    # Create or update assignment
    # ---------------------------------------------
    service = services.AssignmentService()

    assignment = service.get_by_course_assignment_tuple(
        data['course_id'],
        data['assignment_id']
    ).first()

    if assignment is None:
        service.create(data)
    else:
        service.update(assignment.id, data)

    return render(
        request,
        strings.teacher_submission_confirmation
    )


def _submit_assignment(request):
    """Submit the assignment (restricted to students).

    Args:
        request (HttpRequest): The request object.

    Returns:
        JsonResponse: The response object.
    """

    course_id = request.session.get(strings.course_id)
    assignment_id = request.session.get(strings.assignment_id)
    assignment_type = request.session.get(strings.assignment_type)
    outcome_service_url = request.session.get(strings.outcome_service_url)
    result_sourcedid = request.session.get(strings.result_sourcedid)
    attempts = request.session.get('{}_{}_attempts'.format(course_id, assignment_id))

    text = request.POST.get('text')
    service = services.AssignmentService()

    result = django_rq.enqueue(
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

    return JsonResponse({'assignment_type': assignment_type})
