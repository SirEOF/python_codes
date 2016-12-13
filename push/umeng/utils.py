# coding=utf-8
import json
import threading
from functools import wraps

import os
from django.conf import settings

###################################################################################
TEST_SWITCH = settings.DEBUG  # set production mode the same to production debug.
###################################################################################

DEFAULT_ALIAS_TYPE = '**'
LOG_FILE = os.path.join(settings.BASE_DIR, "../log", "umeng.log")


class Type(object):
    UNICAST = 'unicast'
    LISTCAST = 'listcast'
    FILECAST = 'filecast'
    GROUPCAST = 'groupcast'
    BROADCAST = 'broadcast'
    CUSTOMIZEDCAST = 'customizedcast'


class DisplayType(object):
    NOTIFICATION = 'notification'
    MESSAGE = 'message'


class AfterOpen(object):
    GO_APP = 'go_app'
    GO_URL = 'go_url'
    GO_ACTIVITY = 'go_activity'
    GO_CUSTOM = 'go_custom'


class OpenActionType(object):
    MARKET = 'market'  # 车市主页
    CAR_DETAIL = 'detail'  # 车辆详情页
    RECKON = 'reckon'  # 估值页
    BILLBOARD = 'billboardtype'  # 榜单页面


class AppType(object):
    DEALER = 'dealer'
    CUSTOMER = 'customer'
    ENTERPRICE = 'enterprice'


def get_umeng_logger():
    import logging
    import logging.handlers
    um_logger = logging.getLogger('mylogger')
    um_logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    um_logger.addHandler(fh)
    return um_logger


def log_wrapper(function_name):
    logger = get_umeng_logger()
    import inspect
    def umeng_logger(func):
        @wraps(func)
        def umeng_func(*args, **kwargs):
            rtn = func(*args, **kwargs)
            arg_names = inspect.getargspec(func)[0]
            params = {n: a for n, a in zip(arg_names, args)}
            params.update(kwargs)
            log_msg = ' '.join([str(k) + '=' + json.dumps(v, ensure_ascii=False) for k, v in params.items()])
            logger.info(function_name + ' ' + log_msg)
            return rtn

        return umeng_func

    return umeng_logger


def async(func):
    """ Decorator that turns a callable function into a thread."""

    @wraps(func)
    def async_func(*args, **kwargs):
        thread = threading.Thread(
            target=func,
            args=args,
            kwargs=kwargs
        )
        thread.start()

    return async_func
