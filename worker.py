import os
import sys

import django
import redis
from redis import Redis
import urllib
from rq import Worker, Queue, Connection

settings = 'scriba.settings.production'

if len(sys.argv) > 1 and sys.argv[1] == '--settings':
    settings = sys.argv[2]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

django.setup()

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

# redis_url = os.getenv('REDISTOGO_URL')

urllib.parse.uses_netloc.append('redis')
url = urllib.parse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

# conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
