# coding=utf-8
import logging


def get_logger(name, path=None, level=logging.INFO):
    """
    获取logger
    :param name: str 名称
    :param path: str 路径
    :param level: logging.LEVEL 日志级别
    :return: logging.Logger 日志对象
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    if path:
        handler = logging.FileHandler(path)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)
    if logger.level == logging.NOTSET or logger.level > level:
        logger.setLevel(level)
    return logger

