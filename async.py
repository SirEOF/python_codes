# coding=utf-8
import Queue
import threading
from functools import wraps


class ThreadSafeCounter():
    """ 同步计数器
    """

    def __init__(self, counter=0, dec_trigger_dic=None):
        """
        :param counter: 计数器初始值
        :param dec_call_back: 计数器减法触发器字典
        """
        self.lock = threading.Lock()
        self.counter = counter
        self.dec_trigger_dic = dec_trigger_dic or {}

    def increment(self):
        with self.lock:
            self.counter += 1

    def decrement(self):
        with self.lock:
            self.counter -= 1
            call_back = self.dec_trigger_dic.get(self.counter)
            if call_back:
                call_back()


class ThreadPool:
    """ 线程池
    """

    class TreadPoolException(Exception):
        pass

    class NULLKEY:
        pass

    def __init__(self, worker_limit):
        self.task_queue = Queue.Queue(maxsize=worker_limit)
        self.result_dict = {}
        self.is_join = False

    def setup_func(self, key, func, *args, **kws):
        """ 把func的返回定向到out_dict
        """

        def func_wrap():
            self.result_dict[key] = func(*args, **kws)
            self.task_queue.get()
            self.task_queue.task_done()

        def func_origin():
            func(*args, **kws)
            self.task_queue.get()
            self.task_queue.task_done()

        if key != self.NULLKEY:
            return func_wrap
        else:
            return func_origin

    def putting_task(self, func, *args, **kws):
        """ 向队列中放置任务
        """
        if self.is_join:
            raise self.TreadPoolException('Thread pool is closed.')
        result_id = kws.pop('_result_id', self.NULLKEY)
        task = self.setup_func(result_id, func, *args, **kws)
        self.task_queue.put(True)
        self.execute_task(task)

    def execute_task(self, task):
        """ 取出队列中的任务执行
        """
        t = threading.Thread(target=task)
        t.start()

    def join(self):
        self.is_join = True
        self.task_queue.join()

    def async(self, func):
        @wraps(func)
        def call_function(*args, **kws):
            self.putting_task(func, *args, **kws)

        return call_function


def multitasking(task_iter, worker_limit=4):
    """ 用于多任务并行, 值为需要并发的函数和对应的参数列表, 所有的函数执行完毕返回结果字典/列表
    :param task_iter: 多任务字典或数组 dict{key(string): value(list[func, args, kws])} or list[list[func, args, kws]]
    :param worker_limit: 多任务线程数目 int
    :return: out_dict: dict{key(string): value}
    """
    if isinstance(task_iter, dict):
        iter_type = 'dict'
    elif isinstance(task_iter, list):
        iter_type = 'list'
    else:
        raise ValueError('Param `task_iter` must be a list or a dict object.')
    pool = ThreadPool(worker_limit=worker_limit)
    if iter_type == 'dict':
        iters = task_iter.items()
    else:
        iters = enumerate(task_iter)
    for k, v in iters:
        assert len(
            v) <= 3, 'Length of list as the value in dict cant be longer than 3.'
        v = {
            1: list(v) + [(), {}],
            2: list(v) + [{}],
            3: v,
        }.get(len(v))
        func, args, kws = v
        kws['_result_id'] = k
        pool.putting_task(func, *args, **kws)
    pool.join()
    out_dict = pool.result_dict
    if iter_type == 'list':
        out_iter = [None] * len(task_iter)
        for i in xrange(len(out_iter)):
            out_iter[i] = out_dict[i]
    else:
        out_iter = out_dict
    return out_iter


def fake_multitasking(task_iter, worker_limit=4):
    """ 用于调试时替换multitasking函数以检查性能瓶颈.
    """
    if isinstance(task_iter, dict):
        out_iter = {}
        iter_type = 'dict'
    elif isinstance(task_iter, list):
        out_iter = [None] * len(task_iter)
        iter_type = 'list'
    else:
        raise ValueError('Param `task_iter` must be a list or a dict object.')
    if iter_type == 'dict':
        iter_items = task_iter.items()
    else:
        iter_items = enumerate(task_iter)
    for k, v in iter_items:
        assert len(
            v) <= 3, 'Length of list as the value in dict cant be longer than 3.'
        v = {
            1: list(v) + [(), {}],
            2: list(v) + [{}],
            3: v,
        }.get(len(v))
        func, args, kws = v
        out_iter[k] = func(*args, **kws)
    return out_iter


def async(func):
    """ 将函数方法转换为异步
    :param func: 函数/方法
    :return: 异步函数
    """
    @wraps(func)
    def async_func(*args, **kwargs):
        thread = threading.Thread(
            target=func,
            args=args,
            kwargs=kwargs
        )
        thread.start()

    return async_func
