from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rq import Queue, registry

from worker import conn


def index(request):
    q = Queue(connection=conn)

    assignment_type = request.session.get('assignment_type')
    job_id = request.session.get('job_id')
    job = q.fetch_job(job_id)

    if job is None or job.result is None:
        return HttpResponse(status=204)

    template = (
        'learner/feedback.html'
        if assignment_type == 'D'
        else 'learner/submission-confirmation.html'
    )

    return render(request, template, job.result)
