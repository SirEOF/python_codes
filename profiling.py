# coding=utf-8

# TODO(weidwonder): 需要实现获取用户自定义方法
import datetime as dt
import imp
import inspect
import operator
import sys
from collections import defaultdict
from functools import wraps
from threading import local

import os
import types

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

    @classmethod
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
        _thread_locals.cur_stack = [FuncNode.root()]
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


def show_timing_cost(node=FuncNode.root(), deep=None, parent_cost=0):
    if node == FuncNode.root():
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


ROOT_DIR = ''


class ProfilingImporter:
    """ Importer
    """

    def __init__(self):
        if not ROOT_DIR:
            raise RuntimeError(u'Please use `install_importer` to install ProfilingImporter')

    def find_module(self, fullname, path=None):
        # Note: we ignore 'path' argument since it is only used via meta_path
        subname = fullname.split(".")[-1]
        if subname != fullname and path is None:
            return None
        try:
            file, filename, etc = imp.find_module(subname, path)
        except ImportError:
            return None
        return ProfilingLoader(fullname, file, filename, etc)


class ProfilingLoader:
    """ ImpLoader
    """
    code = source = None

    def __init__(self, fullname, file, filename, etc):
        self.file = file
        self.filename = filename
        self.fullname = fullname
        self.etc = etc

    def load_module(self, fullname):
        self._reopen()
        try:
            mod = imp.load_module(fullname, self.file, self.filename, self.etc)
        finally:
            if self.file:
                self.file.close()
        # Note: we don't set __loader__ because we want the module to look
        # normal; i.e. this is just a wrapper for standard import machinery
        self.inject_timing(mod)
        return mod

    def get_data(self, pathname):
        return open(pathname, "rb").read()

    def _reopen(self):
        if self.file and self.file.closed:
            mod_type = self.etc[2]
            if mod_type == imp.PY_SOURCE:
                self.file = open(self.filename, 'rU')
            elif mod_type in (imp.PY_COMPILED, imp.C_EXTENSION):
                self.file = open(self.filename, 'rb')

    def inject_timing(self, mod):
        if self.filename.startswith(ROOT_DIR) and self.filename != __file__:
            print 'install ', self.fullname
            for attr in dir(mod):
                if not attr.startswith('__'):
                    rattr = getattr(mod, attr)
                    attr_module = getattr(rattr, '__module__', None)
                    if attr_module == self.fullname:
                        print attr, '>' * 10
                        setattr(mod, attr, wrap_timing(rattr))


def install_importer(root_dir='.'):
    global ROOT_DIR
    ROOT_DIR = os.path.abspath(root_dir)
    importer = ProfilingImporter()
    sys.meta_path = [importer]


def wrap_timing(obj):
    if getattr(obj, '__name__', '').startswith('__'):
        return obj
    if inspect.isclass(obj):
        for attr in dir(obj):
            if not attr.startswith('__'):
                setattr(obj, attr, wrap_timing(getattr(obj, attr)))
        return obj
    if inspect.ismethod(obj) or inspect.isfunction(obj):
        return timing(obj)
    return obj

def activate_timing(_locals):
    for name, attr in _locals.items():
        if hasattr(attr, '__module__'):
            if attr.__module__ == '__main__':
                _locals[name] = wrap_timing(attr)
