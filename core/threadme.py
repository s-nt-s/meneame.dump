from queue import Queue
from threading import Thread

from .util import chunks

def _do_work(q, rt):
    while not q.empty():
        args = q.get()
        fnc = args[0]
        r = fnc(*args[1:])
        if r:
            rt.append(r)
        q.task_done()
    return True

class ThreadMe:
    def __init__(self, data, do_work, fix_param=None, max_thread=10):
        self.max_thread = max_thread
        self.data = data
        if fix_param is None:
            fix_param = tuple()
        elif not isinstance(fix_param, tuple):
            fix_param = (fix_param, )
        self.fix_param = (do_work, ) + fix_param

    def run(self):
        for dt in chunks(self.data, self.max_thread):
            q = Queue(maxsize=0)
            rt = []
            for d in dt:
                q.put(self.fix_param + (d, ))
            for i in range(len(dt)):
                worker = Thread(target=_do_work, args=(q, rt))
                worker.setDaemon(True)
                worker.start()
            q.join()
            yield rt
