#conding:utf-8
import collections
import functools
import threading
import time
import redis

class ControlSpeed(object):

    def __init__(self, max_calls, period=1.0, callback=None):
        if period <= 0:
            raise ValueError('Speed limiting period must be > 0')
        if max_calls <= 0:
            raise ValueError('Speed limiting number of calls must be > 0')

        self.calls = collections.deque()

        self.period = period
        self.max_calls = max_calls
        self.callback = callback

    def __call__(self, f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                return f(*args, **kwargs)
        return wrapped

    def __enter__(self):
        if len(self.calls) >= self.max_calls:
            until = time.time() + self.period - self._timespan
            last = self._timespan
            if last >= self.period:
                until = 0
            else:
                until = self.period - last
            if self.callback:
                t = threading.Thread(target=self.callback, args=(until,))
                t.daemon = True
                t.start()
            time.sleep(until)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.calls.append(time.time())
        #beyond period,pop deque
        while len(self.calls) > self.max_calls:
            self.calls.popleft()

    @property
    def _timespan(self):
        return self.calls[-1] - self.calls[0]

    @property
    def _lastpoint(self):
        return time.time() - self.calls[-1]

class ControlSpeedNetwork(object):

    def __init__(self,redis_conn, key, max_calls, period=1.0, callback=None):
        if period <= 0:
            raise ValueError('Speed limiting period must be > 0')
        if max_calls <= 0:
            raise ValueError('Speed limiting number of calls must be > 0')

        self.key = key
        self.redis_conn = redis_conn

        self.period = period
        self.max_calls = max_calls
        self.callback = callback

    def __call__(self, f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                return f(*args, **kwargs)
        return wrapped

    def __enter__(self):
        if self.redis_conn.llen(self.key) >= self.max_calls:
            until = time.time() + self.period - self._timespan
            last = self._timespan
            if last >= self.period:
                until = 0
            else:
                until = self.period - last
            if self.callback:
                t = threading.Thread(target=self.callback, args=(until,))
                t.daemon = True
                t.start()
            time.sleep(until)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.redis_conn.rpush(self.key,time.time())
        while self.redis_conn.llen(self.key) > self.max_calls:
            self.redis_conn.lpop(self.key)

    @property
    def _timespan(self):
        return float(self.redis_conn.lrange(self.key,-1,-1)[0]) - float(self.redis_conn.lrange(self.key,0,0)[0])

    @property
    def _lastpoint(self):
        return time.time() - float(self.redis_conn.lrange(self.key,-1,-1)[0])

