import os
import sys

import django
import urllib
from redis import Redis
from rq import Queue, Connection
from rq.worker import HerokuWorker as Worker

settings = 'scriba.settings.production'

if len(sys.argv) > 1 and sys.argv[1] == '--settings':
    settings = sys.argv[2]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

django.setup()

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL')
if not redis_url:
    raise RuntimeError('Set up Redis To Go first.')

urllib.parse.uses_netloc.append('redis')
url = urllib.parse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
