# coding=utf-8
from __future__ import absolute_import

from .android_api import UMengAndroid
from .ios_api import UMengIOS
from .utils import log_wrapper

ANDROID = 'android'
IOS = 'ios'

class UMengMsg(object):
    @staticmethod
    @log_wrapper('SEND-ALIAS')
    def send_alias(app_type, alias_type, alias, ticker, title, text, device_type=None, extra=None, **kws):
        """ 推送消息,
        :param app_type: app类型 AppType.DEALER (车商版)或 AppType.CUSTOMER (个人版)
        :param alias_type: alias类型 'gongpingjia'
        :param alias: alias(device_code)或file_id(文件id)
        :param ticker: 通知栏提示文字
        :param title: 通知标题
        :param text: 通知文字描述
        :param device_type: 设备类型, ANDROID 或 IOS
        :param extra: 附加字段(字典类型), 一般用来指定推送后打开动作, 亦可以包含推送类内的其他参数, 详见 https://trello.com/c/XrUso9jl/1-extra
        :return: None
        """
        if device_type:
            if device_type == ANDROID:
                UMengAndroid.customcast(app_type, ticker, title, text, alias, alias_type, extra=extra, **kws)
            if device_type == IOS:
                UMengIOS.customized_cast(ticker, title + ' ' + text, title + ' ' + text, alias, app_type, alias_type, extra=extra, **kws)
        else:
            UMengAndroid.customcast(app_type, ticker, title, text, alias, alias_type, extra=extra)
            UMengIOS.customized_cast(ticker, title + ' ' + text, title + ' ' + text, alias, app_type, alias_type, extra=extra)
        return

    @staticmethod
    @log_wrapper('UPLOAD-FILE')
    def upload_alias(app_type, alias, device_type=None):
        if device_type:
            if device_type == ANDROID:
                file_id = UMengAndroid.upload_alias(app_type, alias)
            elif device_type == IOS:
                file_id = UMengIOS.upload_alias(app_type, alias)
            else:
                raise ValueError('device_type wrong.')
        else:
            file_id = {}
            file_id[ANDROID] = UMengAndroid.upload_alias(app_type, alias)
            file_id[IOS] = UMengIOS.upload_alias(app_type, alias)
        return file_id
