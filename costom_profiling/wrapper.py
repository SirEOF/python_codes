# coding=utf-8
import datetime
import inspect
from collections import defaultdict
from threading import local

import os

from costom_profiling.settings import SETTINGS

tree = defaultdict(lambda: tree, children=[])

timing_dict = tree

_thread_locals = local()

stacks = []

current_path = os.path.abspath(os.path.join(__file__, os.path.pardir))


class FuncNode(object):
    """ function node
    """

    fn_map = {
        # id(fn): [fn, call_times]
        0: [None, 1],
    }

    @classmethod
    def register_fn(cls, frame):
        frame_info = cls.fn_map.setdefault(id(frame), [frame, 0])
        frame_info[1] += 1
        cls.fn_map[id(frame)] = frame_info
        return frame_info

    def __init__(self, frame, children=None, cost=0):
        if frame is not None:
            fn_info = self.register_fn(frame)
            self.id = str(id(frame)) + ':' + str(fn_info[1])
        else:
            self.id = 0
        self.children = children or []
        self.cost = cost
        self.frame = frame

        self.start = None
        self.end = None

    @classmethod
    def root(cls):
        return cls(None)

    def is_root(self):
        return self.id == 0

    def __repr__(self):
        if self.frame is None:
            return 'root' + ':' + str(self.cost)
        return self.frame.f_code.co_name + ':' + str(self.cost)

    __str__ = __repr__

    def __eq__(self, other):
        return self.frame is other.frame


class Profile:

    is_function = staticmethod(inspect.isfunction)

    def _get_stack(self):
        """ get current thread user defined call stack.
        """
        if not hasattr(_thread_locals, 'cur_stack'):
            new_stack = [FuncNode.root()]
            stacks.append(new_stack)
            _thread_locals.cur_stack = new_stack
        return _thread_locals.cur_stack

    def profiler(self, frame, event, func):
        """ profile the func 
        """
        frame_filename = frame.f_code.co_filename
        if (func is None or not self.is_function(func) or not SETTINGS['PROFILING_START']
            or not frame_filename.startswith(SETTINGS['ROOT_DIR']) or frame_filename.startswith(current_path)):
            return
        stack = self._get_stack()
        if event in ('call', 'c_call'):
            node = FuncNode(frame)
            parent = stack[-1]
            parent.children.append(node)
            stack.append(node)
            node.start = datetime.datetime.now()

        elif event in ('return', 'c_return', 'exception', 'c_exception') and len(stack) > 1:
            node = stack.pop()
            node.end = datetime.datetime.now()
            time_cost = node.end - node.start
            node.cost = time_cost.total_seconds
