# coding=utf-8
from __future__ import absolute_import

import hashlib
import json
import time
import urllib2

import requests

from dict_utils import clean_dict
from .error import UMengException
from .utils import Type, DisplayType, TEST_SWITCH, AfterOpen, DEFAULT_ALIAS_TYPE, async

KEYS = {
    'customer': {
        'app_key': '**',
        'master_secret': '**',
        'message_secret': '**',
    },
    'dealer': {
        'app_key': '**',
        'master_secret': '**',
        'message_secret': '**',
    },
    'enterprice': {
        'app_key': '**',
        'master_secret': '**',
        'message_secret': '**',
    }
}


class UMengAndroid(object):
    SEND_URL = 'http://msg.umeng.com/api/send'
    UPLOAD_URL = 'http://msg.umeng.com/upload'
    METHOD = 'POST'
    TEST_SWITCH = TEST_SWITCH

    def __init__(self, m_type, app_type, display_type, ticker, title, text, after_open=AfterOpen.GO_APP, **kws):
        self.play_vibrate = True
        self.play_sound = True
        self.play_lights = True
        self.async = False
        for k, v in kws.items():
            setattr(self, k, v)
        self.m_type = m_type
        self.app_key, self.master_secret, self.message_secret = self.get_secret(app_type)
        self.timestamp = None
        self.display_type = display_type
        self.ticker = ticker
        self.title = title
        self.text = text
        self.after_open = after_open
        self.extra = self.extra or {}

    def __getattr__(self, item):
        return None

    @staticmethod
    def get_sign(url, post_body, master_secret, method=METHOD):
        s = '%s%s%s%s' % (method, url, post_body, master_secret)
        m = hashlib.md5(s)
        return m.hexdigest()

    @staticmethod
    def get_secret(app_type):
        keys = KEYS[app_type]
        return keys['app_key'], keys['master_secret'], keys['message_secret']

    @staticmethod
    def get_timestamp():
        timestamp = int(time.time() * 1000)
        return timestamp

    def check(self):
        pass

    @staticmethod
    def get_error(e):
        if isinstance(e, urllib2.HTTPError):
            code_or_msg = json.loads(e.read()).get('data', {}).get('error_code', 0)
        elif isinstance(e, basestring):
            code_or_msg = json.loads(e).get('data', {}).get('error_code', 0)
        else:
            code_or_msg = str(e)
        return UMengException(code_or_msg)

    def get_request_json(self):
        timestamp = self.get_timestamp()
        body = clean_dict({
            'ticker': self.ticker,  # 必填 通知栏提示文字
            'title': self.title,  # 必填 通知标题
            'text': self.text,  # 必填 通知文字描述
            # 自定义通知图标:
            'icon': self.icon,  # 可选 状态栏图标ID
            'largeIcon': self.largeIcon,  # 可选 通知栏拉开后左侧图标ID
            'img': self.image,  # 可选 通知栏大图标的URL链接。该字段的优先级大于largeIcon。
            # 自定义通知声音:
            'sound': self.sound,  # 可选 通知声音

            # 自定义通知样式:
            'builder_id': self.build_id,  # 可选 默认为0，用于标识该通知采用的样式。

            # 通知到达设备后的提醒方式
            'play_vibrate': str(self.play_vibrate).lower(),  # 可选 收到通知是否震动,默认为'true'.
            'play_lights': str(self.play_lights).lower(),  # 可选 收到通知是否闪灯,默认为'true'
            'play_sound': str(self.play_sound).lower(),
            # 点击'通知'的后续行为，默认为打开app。
            'after_open': self.after_open,  # 必填 值可以为 AFTER_OPEN
            'url': self.url,  # 可选 当'after_open'为'go_url'时，必填。
            'activity': self.activity,  # 可选 当'after_open'为'go_activity'时，必填。
            "custom": self.custom,  # 可选 display_type=message, 或者
            # display_type=notification且
            # "after_open"为"go_custom"时，
            # 该字段必填。用户自定义内容, 可以为字符串或者JSON格式。
        })
        extra = clean_dict({
            'not_feed_back': 'true'  # 此字段用以区分客服反馈消息, 不可删除
            # 'q': 'q'
        })
        extra.update(clean_dict(self.extra))
        payload = {
            'display_type': self.display_type,
            'body': body,
            'extra': extra,
        }
        policy = clean_dict({
            'start_time': self.start_time,  # 可选 定时发送时间，若不填写表示立即发送.格式YYYY-MM-DD HH:mm:ss
            'expire_time': self.expire_time,  # 可选 消息过期时间,其值不可小于发送时间或者, 默认三天
            'max_send_num': self.max_send_num,  # 可选 发送限速，每秒发送的最大条数。
            'out_biz_no': self.out_biz_no,  # 可选 开发者对消息的唯一标识，服务器会根据这个标识避免重复发送
        })
        request_params = clean_dict({
            'appkey': self.app_key,  # 必填,应用唯一标识
            'timestamp': timestamp,  # 必填,时间戳，10位或者13位均可，时间戳有效期为10分钟
            'type': self.m_type,  # 必填 消息发送类型,其值可以为TYPE一种
            'device_tokens': self.device_tokens,  # 可选 设备唯一表示, 多个使用逗号间隔
            'alias': self.alias,  # 可选 当type=customizedcast时, 开发者填写自己的alias。
            'alias_type': self.alias_type,  # 可选 当type=customizedcast时，必填，alias的类型
            'file_id': self.file_id,  # 可选 当type=filecast时，file内容为多条device_token
            'filter': self.filter,  # 可选 终端用户筛选条件,如用户标签、地域、应用版本以及渠道等
            'payload': payload,
            'policy': policy,
            'production_mode': str(not self.TEST_SWITCH).lower(),  # 可选 正式/测试模式。测试模式下，只会将消息发给测试设备。
            'description': self.description,
            'thirdparty_id': self.thirdparty_id  # 可选 开发者自定义消息标识ID, 开发者可以为同一批发送的多条消息
        })
        request_body = json.dumps(request_params)
        return request_body

    def send(self):
        def _send():
            self.check()
            request_body = self.get_request_json()
            # url, post_body, master_secret, method=METHOD
            sign = self.get_sign(self.SEND_URL, request_body, self.master_secret)
            try:
                r = urllib2.urlopen(self.SEND_URL + '?sign=' + sign, data=request_body)
            except Exception as e:
                raise self.get_error(e)

        if self.async:
            _send = async(_send)
        return _send()

    @staticmethod
    def get_versions_filter(version):
        if version is not None:
            if isinstance(version, basestring):
                version = [version, ]
            elif not isinstance(version, list):
                raise ValueError('version must be None or a string or a list of string.')

        m_filter = None
        if version:
            app_versions = [{"app_version": ver} for ver in version]
            m_filter = {
                "where": {
                    "and": [
                        {
                            "or": app_versions,
                        }
                    ]
                }
            }
        return m_filter

    @staticmethod
    def get_alias_or_tokens(alias_or_tokens):
        if isinstance(alias_or_tokens, basestring):
            alias_or_tokens = alias_or_tokens
        elif isinstance(alias_or_tokens, list):
            alias_or_tokens = ','.join(alias_or_tokens)
        else:
            raise ValueError('alias must be a string or a list of string.')
        return alias_or_tokens

    @classmethod
    def broadcast(cls, app_type, ticker, title, text, extra=None):
        m_type = Type.BROADCAST
        msg = cls(m_type, app_type, DisplayType.NOTIFICATION, ticker, title, text, extra=extra)
        msg.send()

    @classmethod
    def groupcast(cls, app_type, ticker, title, text, version, extra=None):
        m_type = Type.GROUPCAST
        m_filter = cls.get_versions_filter(version)
        msg = cls(m_type, app_type, DisplayType.NOTIFICATION, ticker, title, text, filter=m_filter, extra=extra)
        msg.send()

    @classmethod
    def customcast(cls, app_type, ticker, title, text, alias, alias_type=DEFAULT_ALIAS_TYPE, extra=None, **kws):
        m_type = Type.CUSTOMIZEDCAST
        alias = cls.get_alias_or_tokens(alias)
        msg = cls(m_type, app_type, DisplayType.NOTIFICATION, ticker, title, text, alias_type=alias_type,
                  alias=alias, extra=extra, **kws)
        msg.send()

    @classmethod
    def upload_alias(cls, app_type, alias):
        if isinstance(alias, basestring):
            alias = [alias]
        app_key, master_secret, _ = cls.get_secret(app_type)
        content = {
            "appkey": cls.get_secret(app_type)[0],
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
    # UMengAndroid.customcast('customer', '测试信息', '测试信息', '测试信息', 'ffffffff-f5aa-be68-ffff-ffff9612c2b0',
    # 'gongpingjia', extra={'type': 'promo'}, version='2.5.0')
    # UMengAndroid.customcast('dealer', '测试信息', '测试信息', '测试信息', 'ffffffff-f14c-861f-bdaa-c8ac0033c587',
    # 'gongpingjia', extra={'type': 'promo'})
    # UMengAndroid.groupcast('customer', '测试消息', '测试', '消息', '2.7.0', extra={'type': 'detail',
    # 'typevalue': '31473869'})
    # print UMengAndroid.upload_alias('customer', ['123', ])
    pass
