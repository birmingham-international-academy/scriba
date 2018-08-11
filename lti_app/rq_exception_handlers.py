import django_rq


def inflate_exception(job, exc_type, exc_value, traceback):
    job.meta['exception'] = exc_value
    job.save_meta()
    return True

def move_to_failed_queue(job, *exc_info):
    worker = django_rq.get_worker()
    worker.move_to_failed_queue(job, *exc_info)
    return True
