# coding=utf-8
import datetime as dt
import operator
from collections import defaultdict
from functools import wraps
from threading import local

import types
from django.views.generic import View

from classproperty import classproperty

tree = defaultdict(lambda: tree, children=[])

timing_dict = tree

_thread_locals = local()


class FuncNode(object):
    """ function node
    """

    fn_map = {
        # id(fn): [fn, call_times]
        0: [None, 1],
    }

    __root = None

    @classmethod
    def register_fn(cls, fn):
        fn_info = cls.fn_map.setdefault(id(fn), [fn, 0])
        fn_info[1] += 1
        cls.fn_map[id(fn)] = fn_info
        return fn_info

    def __init__(self, fn, children=None, cost=0):
        if fn is not None:
            fn_info = self.register_fn(fn)
            self.id = str(id(fn)) + ':' + str(fn_info[1])
        else:
            self.id = 0
        self.children = children or []
        self.cost = cost
        self.fn = fn

    @classproperty
    def root(cls):
        if not cls.__root:
            cls.__root = cls(None)
        return cls.__root

    def __repr__(self):
        if self.fn is None:
            return 'root' + ':' + str(self.cost)
        return self.fn.__name__ + ':' + str(self.cost)

    __str__ = __repr__


def get_stack():
    """ get current thread user defined call stack.
    """
    if not hasattr(_thread_locals, 'cur_stack'):
        _thread_locals.cur_stack = [FuncNode.root]
    return _thread_locals.cur_stack


def timing(func):
    @wraps(func)
    def wrap_func(*args, **kws):
        stack = get_stack()
        node = FuncNode(func)
        parent = stack[-1]
        parent.children.append(node)
        stack.append(node)

        start = dt.datetime.now()
        rtn = func(*args, **kws)
        end = dt.datetime.now()

        stack.pop()
        time_cost = end - start
        node.cost = time_cost.total_seconds()
        return rtn

    return wrap_func


def show_timing_cost(node=FuncNode.root, deep=None, parent_cost=0):
    if node == FuncNode.root:
        node.cost = sum([_.cost for _ in node.children])

    # calculate cost percent of parent
    cost_percent = ''
    if parent_cost:
        cost_percent = str(round((node.cost * 100.0) / parent_cost, 2)) + '%'

    deep = deep or []

    ver_con = '│   '
    ver_des = '    '
    tab_option = [ver_con, ver_des]
    child_con = '├───'
    child_des = '└───'

    print '%(name)-25s: %(cost_percent)5s %(cost)8s(S)' % dict(name=getattr(node.fn, '__name__', 'root'),
                                                                 cost_percent=cost_percent, cost=node.cost)
    cur_children = sorted(node.children, key=operator.attrgetter('cost'), reverse=True)
    max_index = len(cur_children) - 1
    for i, c in enumerate(cur_children):
        done = i == max_index
        start_char = child_des if done else child_con
        print ''.join([tab_option[_] for _ in deep]) + start_char,
        show_timing_cost(c, deep=deep + [done], parent_cost=c.cost)


def view_timing(view):
    for attr_name in set(dir(view)) - set(dir(View)):
        attr = getattr(view, attr_name)
        if isinstance(attr, types.MethodType):
            setattr(view, attr_name, timing(attr))
    return view
