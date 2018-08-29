import django_rq
from django.http import HttpResponse
from django.shortcuts import render

from lti_app import strings


def index(request):
    q = django_rq.get_queue()

    # Retrieve job data
    # ---------------------------------------------
    job_id = request.session.get(strings.job_id)
    job = q.fetch_job(job_id)
    data = job.result

    if job is None or data is None and not job.is_failed:
        return HttpResponse(status=204)

    if job.is_failed:
        return render(request, strings.ajax_500, {
            'exception': job.meta['exception']
        })

    # Update attempts
    # ---------------------------------------------
    course_id = request.session.get(strings.course_id)
    assignment_id = request.session.get(strings.assignment_id)
    attempts_key = '{}_{}_attempts'.format(course_id, assignment_id)
    attempts = request.session.get(attempts_key)

    if attempts is None:
        attempts = 1
    else:
        attempts += 1

    request.session[attempts_key] = attempts

    # Update latest feedback
    # ---------------------------------------------
    data_copy = dict(data)
    data_copy.pop('assignment', None)

    request.session[strings.latest_feedback] = data_copy

    # Return response
    # ---------------------------------------------

    template = strings.learner_ajax_feedback

    return render(request, template, data)
