from django.http import HttpResponse
from django.shortcuts import render
from rq import Queue

from worker import conn


def index(request):
    q = Queue(connection=conn)

    assignment_type = request.session.get('assignment_type')
    job_id = request.session.get('job_id')
    job = q.fetch_job(job_id)
    data = job.result

    if job is None or data is None and not job.is_failed:
        return HttpResponse(status=204)

    if job.is_failed:
        return render(request, '500-ajax.html')

    if assignment_type == 'D':
        template = 'learner/feedback-ajax.html'
    else:
        template = 'learner/submission-confirmation.html'

    return render(request, template, data)
