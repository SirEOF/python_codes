# -*-coding: utf-8 -*-
from __future__ import absolute_import
import time
import hashlib
import json
import urllib2
import requests

from .error import UMengException
from .utils import async, TEST_SWITCH
from utils.common.dict_utils import clean_dict

CUSTOMER_KEY = {  # 个人版
    'appkey': '**',
    'app_master_secret': '**',
}

DEALER_KEY = {  # 商家版
    'appkey': '**',
    'app_master_secret': '**',
}

ENTERPRICE_KEY = {
    'appkey': '**',
    'app_master_secret': '**',
}

KEY_DIC = {
    'dealer': DEALER_KEY,
    'customer': CUSTOMER_KEY,
    'enterprice': ENTERPRICE_KEY,
}


class UMengIOS(object):
    """
    Class that push message to ios user.
    """
    SEND_URL = 'http://msg.umeng.com/api/send'
    UPLOAD_URL = 'http://msg.umeng.com/upload'
    METHOD = 'POST'
    TEST_SWITCH = TEST_SWITCH

    def __init__(self, m_type, alert, user_type, extra=None, **kwargs):
        self.sound = 'default'
        self.async = False
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.m_type = m_type
        self.alert = alert
        self.appkey, self.app_master_secret = self.get_key_and_secret(user_type)
        self.extra = extra or {}
        self.check_attr()

    def __getattr__(self, item):
        return None

    @staticmethod
    def get_sign(url, post_body, master_secret, method=METHOD):
        s = '%s%s%s%s' % (method, url, post_body, master_secret)
        m = hashlib.md5(s)
        return m.hexdigest()

    @staticmethod
    def get_key_and_secret(user_type):
        return KEY_DIC[user_type]['appkey'], KEY_DIC[user_type]['app_master_secret']

    def check_attr(self):
        pass

    @staticmethod
    def get_timestamp():
        timestamp = int(time.time() * 1000)
        return timestamp

    def get_request_json(self):
        timestamp = self.get_timestamp()
        aps_dict = clean_dict({
            'alert': self.alert,
            'badge': self.badge,
            'sound': self.sound,
            'content-available': self.content_available,
            'category': self.category,
        })
        payload_dict = clean_dict({
            'aps': aps_dict
        })
        payload_dict.update(self.extra)
        policy_dict = clean_dict({
            'start_time': self.start_time,
            'expire_time': self.expire_time,
            'max_send_num': self.max_send_num,
        })
        request_dict = clean_dict({
            'appkey': self.appkey,
            'timestamp': timestamp,
            'alias_type': self.alias_type,
            'alias': self.alias,
            'type': self.m_type,
            'device_tokens': self.device_tokens,
            'file_id': self.file_id,
            'payload': payload_dict,
            'filter': self.filter,
            'policy': policy_dict,
            'description': self.description,
            'thirdparty_id': self.thirdparty_id,
        })
        request_dict.update({
            'production_mode': not self.TEST_SWITCH,
        })
        request_json = json.dumps(request_dict)
        return request_json

    @classmethod
    def customized_cast(cls, ticker, title, text, alias, app_type, alias_type, extra=None, **kwargs):
        if isinstance(alias, basestring):
            alias = alias
        elif isinstance(alias, list):
            alias = ','.join(alias)
        else:
            raise ValueError('alias type is neither a string nor a list.')
        body = {
            'ticker': ticker,
            'title': title,
            'text': text,
        }
        extra['body'] = body
        msg = cls('customizedcast', title, app_type, alias=alias, alias_type=alias_type, extra=extra, **kwargs)
        msg.send()

    def send(self):
        def _send():
            request_json = self.get_request_json()
            sign = self.get_sign(self.SEND_URL, request_json, self.app_master_secret)
            try:
                r = urllib2.urlopen(self.SEND_URL + '?sign=' + sign, data=request_json)
            except Exception as e:
                raise self.get_error(e)

        if self.async:
            _send = async(_send)
        return _send()

    def get_error(self, e):
        if isinstance(e, urllib2.HTTPError):
            code_or_msg = json.loads(e.read()).get('data', {}).get('error_code', 0)
        else:
            code_or_msg = e.reason
        return UMengException(code_or_msg)

    @classmethod
    def upload_alias(cls, app_type, alias):
        if isinstance(alias, basestring):
            alias = [alias]
        app_key, master_secret = cls.get_key_and_secret(app_type)
        content = {
            "appkey": cls.get_key_and_secret(app_type)[0],
            "timestamp": cls.get_timestamp(),
            "content": '\r\n'.join(alias)  # 必填 文件内容,多个device_token/alias请用回车符"\n"分隔。
        }
        content = json.dumps(content)
        sign = cls.get_sign(cls.UPLOAD_URL, content, master_secret)
        try:
            r = requests.post(cls.UPLOAD_URL + '?sign=' + sign, data=content)
            r_dic = json.loads(r.content)
            if r.status_code != 200:
                if r_dic['ret'] == 'FAIL':
                    code = int(r_dic['data']['error_code'])
                    raise UMengException(code)
            else:
                return r_dic['data']['file_id']
        except UMengException as e:
            raise e
        except Exception as e:
            raise e


if __name__ == '__main__':
    appkey = '**'
    app_master_secret = '**'
    alias_type = "**"
    alias = "**"  # iphone 5s
    ticker = "**"
    extra = {
        # 'display_type': 'notification',
        'type': '**',  # 抢好车的主页面
        'forcejump': '**',
        'typevalue': '**',
    }
    '''ticker, title, text, alias, app_type, alias_type, extra=extra'''
    UMengIOS.customized_cast(ticker, '测试', 'text>>', alias, 'customer', alias_type, extra=extra)
    # print UMengIOS.upload_alias('customer', ['123'])
