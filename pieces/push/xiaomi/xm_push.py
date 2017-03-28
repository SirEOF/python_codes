#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 拷贝自 https://github.com/dreamcog/xiaomi_push.git, 开源大法好啊

import sys
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding("utf-8")


class XMPush(object):
    """ 小米推送
    """

    def __init__(self, secret):
        self._online_url = 'https://api.xmpush.xiaomi.com/v2/message/'
        self._sandbox_url = 'https://sandbox.xmpush.xiaomi.com/v2/message/'
        self._send_url = self._online_url
        self._device = ''
        self.status_url = 'https://api.xmpush.xiaomi.com/v1/trace/message/status'

        self.secret = secret

    def setSandbox(self):
        self._send_url = self._sandbox_url

    def setOnline(self):
        self._send_url = self._online_url

    def device(self, device_type='android'):
        if device_type not in ['android', 'ios']:
            print '//传入的device_type未能识别：%s' % device_type
        self._device = device_type

    def message(self, condition, message):
        """ 推送函数
        message 的字段说明：
            payload						消息内容需要url_encode
            restricted_package_name		包名
            pass_through				0 表示通知栏消息,1 表示透传消息
            title						通知栏展示的通知的标题。
            description					通知栏展示的通知的描述。
            notify_type					-1,1,2,4
            ---更多参见:http://dev.xiaomi.com/doc/?p=533 ---
        """
        if isinstance(message, XMMessage):
            message = message.build()
        if condition.has_key('regid'):
            self.send_url = "%s%s" % (self._send_url, 'regid')
        elif condition.has_key('alias'):
            self.send_url = "%s%s" % (self._send_url, 'alias')
        elif condition.has_key('topic'):
            self.send_url = "%s%s" % (self._send_url, 'topic')
        elif condition.has_key('topics'):
            self.send_url = "%s%s" % (self._send_url, 'topics')
        else:
            self.send_url = "%s%s" % (self._send_url, 'all')

        for key in condition:
            message[key] = condition[key]

        headers = {'Authorization': 'key=%s' % self.secret}
        send_data = urllib.urlencode(message)
        req = urllib2.Request(self.send_url, send_data, headers)
        response = urllib2.urlopen(req)
        data = response.read()
        print data

    def status(self, message_id):
        message = {
            'msg_id': message_id
        }
        send_data = urllib.urlencode(message)
        url = '%s?%s' % (self.status_url, send_data)
        req = urllib2.Request(url)
        req.add_header('Authorization', 'key=%s' % self.secret)
        response = urllib2.urlopen(req)
        data = response.read()
        print data


class XMMessage(object):
    """ 小米消息
    """

    def __init__(self):
        pass

    def __getattr__(self, name):
        def _f(value):
            self.__dict__[name] = value
            return self

        return _f

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def build(self):
        return self.__dict__
