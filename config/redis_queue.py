from rq import Queue
from redis import Redis

def get_queue():
    redis_conn = Redis()
    q = Queue(connection=redis_conn)
    return q

