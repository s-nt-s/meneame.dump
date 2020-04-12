from queue import Queue
from threading import Thread

from .util import chunks

count=0

def _do_work(q, fnc, fix_param, rt, rt_null):
    global count
    while not q.empty():
        args = q.get()
        r = fnc(*(fix_param + args))
        if r is None:
            rt_null.append(args[0] if len(args)==1 else args)
        else:
            if isinstance(r, list):
                rt.extend(r)
            else:
                rt.append(r)
        q.task_done()
    return True

class ThreadMe:
    def __init__(self, fix_param=None, max_thread=10, list_size=2000):
        self.max_thread = max_thread
        if fix_param is None:
            fix_param = tuple()
        elif not isinstance(fix_param, tuple):
            fix_param = (fix_param, )
        self.fix_param = fix_param
        self.list_size = list_size
        self.rt_null = []

    def run(self, do_work, data, return_first=False):
        if return_first:
            for i in next(data):
                yield i
        for dt in chunks(data, self.max_thread):
            q = Queue(maxsize=0)
            rt = []
            for d in dt:
                if not isinstance(d, tuple):
                    d = (d,)
                q.put(d)
            for i in range(len(dt)):
                worker = Thread(target=_do_work, args=(q, do_work, self.fix_param, rt, self.rt_null))
                worker.setDaemon(True)
                worker.start()
            q.join()
            for i in rt:
                yield i

    def list_run(self, *args, **kargv):
        for arr in chunks(self.run(*args, **kargv), self.list_size):
            yield arr
