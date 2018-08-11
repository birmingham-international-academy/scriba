from django.http import HttpResponse
from django.shortcuts import render
from rq import Queue

from lti_app import strings
from worker import conn


def index(request):
    q = Queue(connection=conn)

    # Retrieve job data
    # ---------------------------------------------
    job_id = request.session.get(strings.job_id)
    job = q.fetch_job(job_id)
    data = job.result

    if job is None or data is None and not job.is_failed:
        return HttpResponse(status=204)

    if job.is_failed:
        return render(request, '500-ajax.html')

    # Update attempts and return response
    # ---------------------------------------------
    course_id = request.session.get(strings.course_id)
    assignment_id = request.session.get(strings.assignment_id)
    assignment_type = request.session.get(strings.assignment_type)
    attempts_key = '{}_{}_attempts'.format(course_id, assignment_id)
    attempts = request.session.get(attempts_key)

    if attempts is None:
        attempts = 1
    else:
        attempts += 1

    request.session[attempts_key] = attempts

    if assignment_type == 'D':
        template = 'learner/feedback-ajax.html'
    else:
        template = 'learner/submission-confirmation.html'

    return render(request, template, data)
