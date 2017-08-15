# coding=utf-8
import os


def get_project_root():
    """
    获取项目根路径
    :return: 
    """
    parent = lambda path, count: parent(os.path.dirname(path), count - 1) if count > 0 else path
    project_root = parent(os.path.abspath(__file__), 2)
    return project_root


def init_env():
    os.chdir(get_project_root())
