import os
import sys

import django
import redis
from rq import Worker, Queue, Connection

settings = 'scriba.settings.production'

if len(sys.argv) > 1 and sys.argv[1] == '--settings':
    settings = sys.argv[2]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

django.setup()

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
