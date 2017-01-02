# coding=utf-8
import Queue
import threading
from functools import wraps

import gevent


class ThreadSafeCounter:
    """ 同步计数器
    """

    def __init__(self, counter=0, dec_trigger_dic=None):
        """
        :param counter: 计数器初始值
        :param dec_trigger_dic: 计数器减法触发器字典
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
