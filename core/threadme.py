from queue import Queue
from threading import Thread

from .util import chunks

def _do_work(q, rt):
    while not q.empty():
        args = q.get()
        fnc = args[0]
        r = fnc(*args[1:])
        if r:
            if isinstance(r, list):
                rt.extend(r)
            else:
                rt.append(r)
        q.task_done()
    return True

class ThreadMe:
    def __init__(self, fix_param=None, max_thread=10):
        self.max_thread = max_thread
        if fix_param is None:
            fix_param = tuple()
        elif not isinstance(fix_param, tuple):
            fix_param = (fix_param, )
        self.fix_param = fix_param

    def run(self, do_work, data, return_first=False):
        if return_first:
            for i in next(data):
                yield i
        fix_param = (do_work, ) + self.fix_param
        for dt in chunks(data, self.max_thread):
            q = Queue(maxsize=0)
            rt = []
            for d in dt:
                q.put(fix_param + (d, ))
            for i in range(len(dt)):
                worker = Thread(target=_do_work, args=(q, rt))
                worker.setDaemon(True)
                worker.start()
            q.join()
            for i in rt:
                yield i
