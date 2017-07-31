# coding=utf-8
"""
提供一个简易的序列化对象到文件的包装
"""
import os

from pieces.os_ import mkdir_recursive

try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle
import json


def pdump2file(obj, filename, force_create=False, protocol=0):
    """
    pickle 持久化对象
    :param obj: object 对象
    :param filename: str 文件名
    :param force_create: bool 当文件目录不存在时是否强制创建
    :param protocol: int 协议号
    """
    if force_create:
        dir_name = os.path.split(filename)[0]
        if os.path.exists(dir_name):
            mkdir_recursive(dir_name)
    with open(filename, 'w') as f:
        pickle.dump(obj, f, protocol=protocol)


def pload4file(filename):
    """
    从pickle创建的文件中读取对象
    :param filename: 文件名
    :return: object
    """
    with open(filename, 'r') as f:
        return pickle.load(f)


def jdump2file(obj, filename, force_create=False, **kws):
    """
    json 持久化对象
    :param obj: object 对象
    :param filename: str 文件名
    :param force_create: bool 当文件目录不存在时是否强制创建
    :param kws: dict 其他json.dump需要的参数
    """
    if force_create:
        dir_name = os.path.split(filename)[0]
        if os.path.exists(dir_name):
            mkdir_recursive(dir_name)
    with open(filename, 'w') as f:
        json.dump(obj, f, **kws)


def jload4file(filename):
    """
    从json文件中读取对象
    :param filename: str 文件名
    :return: object
    """
    with open(filename, 'r') as f:
        return json.load(f)
