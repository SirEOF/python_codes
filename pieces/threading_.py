# coding=utf-8
from Queue import Queue
from functools import wraps
import threading_

from concurrent.futures import ThreadPoolExecutor


def async(func):
    """ 将函数方法转换为异步
    :param func: 函数/方法
    :return: 异步函数
    """

    @wraps(func)
    def async_func(*args, **kwargs):
        thread = threading_.Thread(
            target=func,
            args=args,
            kwargs=kwargs
        )
        thread.start()

    return async_func


def asyncd(func):
    """ 将函数方法转换为异步, 并作为守护线程
    :param func: 函数/方法
    :return: 异步函数
    """

    @wraps(func)
    def async_func(*args, **kwargs):
        thread = threading_.Thread(
            target=func,
            args=args,
            kwargs=kwargs
        )
        thread.daemon = True
        thread.start()

    return async_func


def pooled_submit_not_block(num, default_rtn=None):
    """
    线程池并行装饰器 (提交无阻塞)
    :param num: int 并行的线程上限
    :param default_rtn: 默认返回值 
    :return: func 无参装饰器
    """
    executor = ThreadPoolExecutor(max_workers=num)

    def wrapper(func):
        @wraps(func)
        def async_func(*args, **kws):
            executor.submit(func, *args, **kws)
            return default_rtn

        async_func.executor = executor
        async_func.shutdown = executor.shutdown
        return async_func

    return wrapper


def pooled_submit_blocked(num, default_rtn=None):
    """
    线程池并行装饰器 (提交阻塞)
    :param num: int 并行的线程上限
    :param default_rtn: 默认返回值 
    :return: func 无参装饰器
    """
    pool = ThreadPool(worker_limit=num)

    def wrapper(func):
        @wraps(func)
        def async_func(*args, **kws):
            pool.putting_task(func, *args, **kws)
            return default_rtn

        async_func.executor = pool
        async_func.shutdown = pool.join
        return async_func

    return wrapper


pooled = pooled_submit_blocked


class PooledObject(object):
    """
    对象池内的对象
    """

    def __init__(self, pool, obj):
        """
        :param pool: ObjectPool 所属对象池
        :param obj: object 对象
        """
        self.obj = obj
        self.pool = pool

    def __enter__(self):
        return self.obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.objects.put(self.obj)


class ObjectPool(object):
    """
    对象池
    """

    def __init__(self, objects, block=True, timeout=None):
        """
        :param objects: list 对象列表
        :param block: bool 是否是阻塞式
        :param timeout: float 阻塞超时时间(秒)
        """
        self._objects = objects
        self.objects = Queue(len(objects))
        self.block = block
        self.timeout = timeout
        for o in objects:
            self.objects.put(o)

    def get(self):
        """
        获取一个对象池中的对象
        :return: PooledObject 返回并不是真的对象, 而是其封装, 可以通过 `with <rtn_obj> as obj: ... ` 获得其包含的对象, 
            退出上下文管理器作用域之后物品会归还到其原先所在的对象池中
        """
        return PooledObject(self, self.objects.get(block=self.block, timeout=self.timeout))


class NamedLock(object):
    """
    命名锁
        同名锁互斥, 异名不干扰
        目前的实现方式不是很好, 日后再改
    """

    num_locks = 64
    locks = [threading_.Condition() for i in xrange(num_locks)]

    def __init__(self, name):
        self.name = name
        self.index = hash(self.name) % self.num_locks
        self.cond = self.locks[self.index]

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            return getattr(self.cond, item)

    def __enter__(self):
        return self.cond.acquire(1)

    def __exit__(self, *args):
        self.cond.notify()
        return self.cond.release()


class ThreadPool:
    """
    Customized thread pool

    copy from https://github.com/weidwonder/async-iter/blob/master/async_iter/async_iter.py
    """

    class TreadPoolException(Exception):
        pass

    class NULLKEY:
        pass

    def __init__(self, worker_limit):
        self.task_queue = Queue(maxsize=worker_limit)
        self.result_dict = {}
        self.is_join = False

    def setup_func(self, key, func, *args, **kws):
        """ wrap the function, redirect the output to the `result_dict`.
        """

        def func_wrap():
            try:
                self.result_dict[key] = func(*args, **kws)
            except:
                raise
            finally:
                # mark one position in queue is available.
                self.task_queue.get()
                self.task_queue.task_done()

        def func_origin():
            try:
                func(*args, **kws)
            except:
                raise
            finally:
                self.task_queue.get()
                self.task_queue.task_done()

        if key is not self.NULLKEY:
            return func_wrap
        else:
            return func_origin

    def putting_task(self, func, *args, **kws):
        """ put task to the queue
        """
        if self.is_join:
            raise self.TreadPoolException('Thread pool is closed.')
        result_id = kws.pop('_result_id', self.NULLKEY)
        task = self.setup_func(result_id, func, *args, **kws)
        # mark one position in queue has been taken.
        self.task_queue.put(True)
        self.execute_task(task)

    def execute_task(self, task):
        """ execute task by start new thread.
        """
        t = threading_.Thread(target=task)
        t.start()

    def join(self):
        """ wait until all tasks in task_queue done.
        """
        self.is_join = True
        self.task_queue.join()
