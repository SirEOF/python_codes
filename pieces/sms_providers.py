#!/usr/bin/env python
# -*-coding: utf-8 -*-
# 过于重度设计, 不建议使用
import hashlib
import sys

reload(sys)
sys.setdefaultencoding("utf8")

import json
import re
import urllib
import urllib2
from bs4 import BeautifulSoup as bs

SUCCESSFUL_NUM = 0
FAILED_NUM = 0


def get(url, params=None, cookie=None):
    content_type = "application/x-www-form-urlencoded"
    connection = "Keep-Alive"
    headers = {'Content-Type': content_type, 'Connection': connection}
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    urllib2.install_opener(opener)
    param_string = ''
    if params:
        param_string = '?' + '&'.join([str(i) + '=' + str(params[i]) for i in params if params[i]])
    req = urllib2.Request(url + param_string, headers=headers)
    page = urllib2.urlopen(req).read()
    return page


def post(url, params=None, cookie=None):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    urllib2.install_opener(opener)
    params = urllib.urlencode(params)
    req = urllib2.Request(url, params)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Connection', 'Keep-Alive')
    response = urllib2.urlopen(req)
    resp = response.read()
    return resp


class SMSGenerator(type):
    code = {
        # 这是应答状态字典，将在类中抹除并添加为类属性。
        'CONNECT_FIELD': u'网络连接失败',
    }

    @classmethod
    def make_action(cls, name):
        # 行为闭包函数，用来生成行为函数
        def _action(self, **kws):
            # 行为函数，kws可以更新params中定义的参量
            action_name = name
            action = self.__class__.actions[action_name]
            params = self.base_param
            params.update(action.get('params', {}))
            params.update(kws)
            try:
                resp = self.request(action_name, params=params)
            except:
                return u"网络连接失败"
            return self.trans_response(resp, action_name)

        _action.__name__ = name
        return _action

    def __new__(cls, name, bases, attrs):
        cls.clean(attrs)
        bases = (cls.BaseSMS,) if not bases else tuple(list(bases).append(cls.BaseSMS))
        actions = attrs['actions']
        for action in actions:
            attrs[action] = cls.make_action(action)
        if not attrs.get('base_param'):
            attrs['base_param'] = {}
        code = attrs.get('code', {})
        (not code) or attrs.pop('code')
        for c in cls.code:
            attrs[c] = cls.code[c]
        for c in code:
            attrs[c] = code[c]
        return super(SMSGenerator, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def clean(attr):
        actions = attr['actions']
        struct = attr.get('resp_struct') or SMSGenerator.BaseSMS.resp_struct
        base_method = attr.get('base_method', None) or SMSGenerator.BaseSMS.base_method
        if base_method not in ('get', 'post'):
            raise AttributeError('class attribute base_method wrong.')
        for action in actions:
            action = actions[action]
            if action.get('filter', None):
                if not isinstance(action['filter'], list):
                    raise AttributeError('Param \'filter\' must be a list.')
                if struct == 'string':
                    for i in range(len(action['filter'])):
                        action['filter'][i][1] = re.compile(action['filter'][i][1])
            method = action.get('method', None)
            if not method:
                method = SMSGenerator.BaseSMS.base_method
                action['method'] = method
            elif method not in ('post', 'get'):
                raise AttributeError('action ' + action + ' method wrong.')

    class BaseSMS(object):

        # 基变量，每一个行为都传递，可以通过构造函数更新。
        base_param = {
            # 'account': '',
            # 'password': '',
        }

        resp_struct = 'xml'  # 支持三种结构xml, json, string

        # 此成员变量定义了发送短信类的所有行为
        actions = {
            'action_name':  # 行为名称，即动态生成的函数名称，返回一个字典
                {
                    'url': 'url_string',  # 行为地址
                    'method': 'post' or 'get',  # 行为方法
                    'params': {},  # 行为参数，行为函数可以有选择的传递
                    'filter': [],  # 指定返回值，此字段定义了action函数返回那些值
                    # json和xml格式此字段只需要写节点名数组即可，string
                    # 格式需要编写二元组，第一位是返回key，第二是匹配的正则表达式
                }
        }

        base_method = 'post'

        def __init__(self, **kw):
            for k, v in kw.items():
                self.base_param[k] = v

        def request(self, action_name, params=None):
            """
            行为参数的http请求行为。
            """
            if action_name not in self.actions:
                raise RuntimeError('Action ' + action_name + ' doesn\'t exist!')
            params = params or self.actions[action_name]['params']
            url = self.actions[action_name]['url']
            if self.actions[action_name]['method'] == 'post':
                resp = post(url, params=params)
            elif self.actions[action_name]['method'] == 'get':
                resp = get(url, params=params)
            else:
                raise AttributeError('Action ' + action_name + ' method is wrong, please check.')
            return resp

        def trans_response(self, resp, action_name):
            """
            返回值转换函数
            """
            if not self.actions[action_name].get('filter', None):
                return resp
            if self.resp_struct == 'xml':
                resp_bs = bs(resp, 'lxml', from_encoding='utf8')
                ret_dic = {}
                for node in self.actions[action_name]['filter']:
                    result = resp_bs.find_all(node)
                    if result:
                        ret_dic[node] = result[0].string.encode('utf8')
                    else:
                        ret_dic[node] = ''
            elif self.resp_struct == 'json':
                resp_json = json.loads(resp)
                ret_dic = {}
                for key in self.actions[action_name]['filter']:
                    ret_dic[key] = resp_json.get(key, '')
            elif self.resp_struct == 'string':
                ret_dic = {}
                for name, regex in self.actions[action_name]['filter']:
                    result = re.findall(regex, resp)
                    ret_dic[name] = result if result else ''
            else:
                return resp
            return ret_dic


class SMS8002:
    """ 目前只能用来发验证码
    """

    __metaclass__ = SMSGenerator

    resp_status = 'xml'
    base_param = {
        'account': 'xxx',
        'password': 'xxx',
        'userid': 'xxx',
    }
    code = {
        'SUCCESS': u'ok',
        'EMPTY_NAME_PSWORD': u'用户名或密码不能为空',
        'CONTAIN_SQL': u'发送内容包含sql注入字符',
        'NAME_PSWORD_ERR': u'用户名或密码错误',
        'PHONE_EMPTY': u'短信号码不能为空',
        'MESSAGE_EMPTY': u'短信内容不能为空',
        'ILLEGAL_CHAR': u'包含非法字符',
        'BALANCE_LOW': u'对不起，您当前要发送的量大于您当前余额',
        'NOT_ILLEGAL_CHAR': u'未包含非法字符',
        'OTHER_ERR': u'其他错误'
    }
    actions = {
        '_send': {
            'url': 'http://120.25.147.10:8002/sms.aspx',
            'params': {
                'mobile': None,
                'content': None,
                'sendTime': '',
                'action': 'send',
            },
            'filter': ['message', 'remainpoint']
        },
        'status': {
            'url': 'http://120.25.147.10:8002/statusApi.aspx',
            'method': 'post',
            'params': {
                'action': 'query'
            },
        },
        'overage': {
            'url': 'http://120.25.147.10:8002/sms.aspx',
            'method': 'post',
            'params': {
                'action': 'overage'
            },
            'filter': ['message', 'overage']
        },
    }

    def send(self, phones, msg):
        phones_list = []
        if hasattr(phones, '__iter__'):
            for phone in phones:
                phones_list.append(str(phone))
            phones_str = ','.join(phones_list)
        else:
            phones_str = str(phones)
        resp = self._send(mobile=phones_str, content=msg)
        return resp

    def trans_response(self, resp, action_name):
        resp = super(SMS8002, self).trans_response(resp, action_name)
        if action_name == 'status':
            table = bs(resp, "lxml")
            mobile = table.find_all('mobile')
            taskid = table.find_all('taskid')
            status = table.find_all('status')
            receive_time = table.find_all('receivetime')
            error_code = table.find_all('errorcode')

            mobile_all = []
            taskid_all = []
            status_all = []
            receive_time_all = []
            error_code_all = []
            for item in mobile:
                mobile_all.append(item.get_text())
            for item in taskid:
                taskid_all.append(item.get_text())
            for item in status:
                status_all.append(item.get_text())
            for item in receive_time:
                receive_time_all.append(item.get_text())
            for item in error_code:
                error_code_all.append(item.get_text())

            resp = []
            for i in range(len(mobile_all)):
                dic = {"mobile": mobile_all[i],
                       "taskid": taskid_all[i],
                       "status": status_all[i],
                       "received time": receive_time_all[i],
                       "error_code": error_code_all[i],
                       }
                resp.append(dic)
        return resp


class SMS8002Marketing:
    """ 8002营销通道
    """

    __metaclass__ = SMSGenerator

    resp_struct = 'xml'
    base_param = {
        'account': 'xxx',
        'password': 'xxx',
        'userid': 'xxx',
    }
    code = {
        'SUCCESS': u'ok',
        'EMPTY_NAME_PSWORD': u'用户名或密码不能为空',
        'CONTAIN_SQL': u'发送内容包含sql注入字符',
        'NAME_PSWORD_ERR': u'用户名或密码错误',
        'PHONE_EMPTY': u'短信号码不能为空',
        'MESSAGE_EMPTY': u'短信内容不能为空',
        'ILLEGAL_CHAR': u'包含非法字符',
        'BALANCE_LOW': u'对不起，您当前要发送的量大于您当前余额',
        'NOT_ILLEGAL_CHAR': u'未包含非法字符',
        'OTHER_ERR': u'其他错误'
    }
    actions = {
        '_send': {
            'url': 'http://120.25.147.10:8002/sms.aspx',
            'params': {
                'mobile': None,
                'content': None,
                'sendTime': '',
                'action': 'send',
            },
            'filter': ['message', 'remainpoint']
        },
        'status': {
            'url': 'http://120.25.147.10:8002/statusApi.aspx',
            'method': 'post',
            'params': {
                'action': 'query'
            },
        },
        'overage': {
            'url': 'http://120.25.147.10:8002/sms.aspx',
            'method': 'post',
            'params': {
                'action': 'overage'
            },
            'filter': ['message', 'overage']
        },
    }

    def send(self, phones, msg):
        phones_list = []
        if hasattr(phones, '__iter__'):
            for phone in phones:
                phones_list.append(str(phone))
            phones_str = ','.join(phones_list)
        else:
            phones_str = str(phones)
        resp = self._send(mobile=phones_str, content=msg)
        return resp

    def trans_response(self, resp, action_name):
        resp = super(SMS8002Marketing, self).trans_response(resp, action_name)
        if action_name == 'status':
            table = bs(resp, "lxml")
            mobile = table.find_all('mobile')
            taskid = table.find_all('taskid')
            status = table.find_all('status')
            receive_time = table.find_all('receivetime')
            error_code = table.find_all('errorcode')

            mobile_all = []
            taskid_all = []
            status_all = []
            receive_time_all = []
            error_code_all = []
            for item in mobile:
                mobile_all.append(item.get_text())
            for item in taskid:
                taskid_all.append(item.get_text())
            for item in status:
                status_all.append(item.get_text())
            for item in receive_time:
                receive_time_all.append(item.get_text())
            for item in error_code:
                error_code_all.append(item.get_text())

            resp = []
            for i in range(len(mobile_all)):
                dic = {"mobile": mobile_all[i],
                       "taskid": taskid_all[i],
                       "status": status_all[i],
                       "received time": receive_time_all[i],
                       "error_code": error_code_all[i],
                       }
                resp.append(dic)
        return resp


class CLSMS:
    __metaclass__ = SMSGenerator

    resp_struct = 'string'
    base_param = {
        'account': 'xxx',
        'pswd': 'xxx',
    }
    STATUS_CODE = {
        0: u'提交成功',
        101: u'无此用户',
        102: u'密码错误',
        103: u'提交过快',
        104: u'系统忙（因平台侧原因，暂时无法处理提交的短信）',
        105: u'敏感短信（短信内容包含敏感词）',
        106: u'消息长度错（>536或<=0）',
        107: u'包含错误的手机号码',
        108: u'手机号码个数错（群发>50000或<=0;单发>200或<=0）',
        109: u'无发送额度（该用户可用短信数已使用完）',
        110: u'不在发送时间内',
        111: u'超出该账户当月发送额度限制',
        112: u'无此产品，用户没有订购该产品',
        113: u'extno格式错（非数字或者长度不对）',
        115: u'自动审核驳回',
        116: u'签名不合法，未带签名（用户必须带签名的前提下）',
        117: u'IP地址认证错,请求调用的IP地址不是系统登记的IP地址',
        118: u'用户没有相应的发送权限',
        119: u'用户已过期',
    }
    SUCCESS_CODE = 0
    actions = {
        '_send': {
            'url': 'http://222.73.117.156:80/msg/HttpBatchSendSM',
            'params': {
                'mobile': '',
                'msg': '',
                'needstatus': 'true',
                'product': '',
                'extno': '',
            },
        },
        '_query_balance': {
            'url': 'http://222.73.117.156:80/msg/QueryBalance',
            'params': {}
        }
    }

    def send(self, phones, msg):
        phones_list = []
        if hasattr(phones, '__iter__'):
            for phone in phones:
                phones_list.append(str(phone))
            phones_str = ','.join(phones_list)
        else:
            phones_str = str(phones)
        resp = self._send(mobile=phones_str, msg=msg)
        return resp

    def check_balance(self):
        return self._query_balance()

    def trans_response(self, resp, action_name):
        resp = resp.strip()
        resp_list = resp.split('\n')
        time, code = resp_list[0].split(',')
        code = int(code)

        if action_name == '_send':
            resp_dic = {
                'time': time,
                'code': code,
                'msgid': resp_list[1] if len(resp_list) > 1 else '',
                'code_msg': self.STATUS_CODE.get(code, u'未知错误')
            }
        elif action_name == '_query_balance':
            if len(resp_list) > 1:
                products = dict([(line.split(',')[0], line.split(',')[1]) for line in resp_list[1:]])
            else:
                products = {}
            resp_dic = {
                'time': time,
                'code': code,
                'code_msg': self.STATUS_CODE.get(code, u'未知错误'),
                'products': products
            }
        else:
            resp_dic = {}
        return resp_dic


class AiXunSMS:
    """ 尚通短信平台
    后台地址: http://login.dx660.com
    """
    __metaclass__ = SMSGenerator

    resp_struct = 'string'

    USER_NAME = 'xxx'
    PASSWORD = 'xxx'

    base_param = {
        'username': USER_NAME,
        'password': hashlib.md5(USER_NAME + hashlib.md5(PASSWORD).hexdigest()).hexdigest(),
    }
    STATUS_CODE = {
        0: u'失败',
        -1: u'用户名或密码不正确',
        -2: u'必填选项为空',
        -3: u'短信内容0个字节',
        -4: u'0个有效号码',
        -5: u'余额不够',
        -10: u'用户被禁用',
        -11: u'短信内容超过500字',
        -12: u'无扩展权限（ext字段需填空）',
        -13: u'IP校验错误',
        -14: u'内容解析异常',
        -24: u'手机号码超过限定个数',
        -25: u'没有提交权限',
        -990: u'未知错误'
    }

    actions = {
        '_send': {
            'url': 'http://120.55.248.18/smsSend.do',
            'params': {
                'mobile': '',
                'content': '',
                'dstime': '',
                'ext': '',
                'msgid': '',
                'msgfmt': '',
            },
        },
        '_query_balance': {
            'url': 'http://120.55.248.18/balanceQuery.do',
            'params': {}
        }
    }

    def trans_response(self, resp, action_name):
        resp = resp.strip()
        code = int(resp)
        if code > 0:
            return True, code
        else:
            return False, self.STATUS_CODE.get(code, u"未知错误")

    def send(self, phones, msg):
        phones_list = []
        if hasattr(phones, '__iter__'):
            for phone in phones:
                phones_list.append(str(phone))
            phones_str = ','.join(phones_list)
        else:
            phones_str = str(phones)
        success, resp = self._send(mobile=phones_str, content=msg)
        return resp

    def check_balance(self):
        return self._query_balance()


class AiXunSMSMarketing:
    """ 尚通营销短信平台
    后台地址: http://login.dx660.com
    """
    __metaclass__ = SMSGenerator

    resp_struct = 'string'

    USER_NAME = 'xxx'
    PASSWORD = 'xxx'

    base_param = {
        'username': USER_NAME,
        'password': hashlib.md5(USER_NAME + hashlib.md5(PASSWORD).hexdigest()).hexdigest(),
    }
    STATUS_CODE = {
        0: u'失败',
        -1: u'用户名或密码不正确',
        -2: u'必填选项为空',
        -3: u'短信内容0个字节',
        -4: u'0个有效号码',
        -5: u'余额不够',
        -10: u'用户被禁用',
        -11: u'短信内容超过500字',
        -12: u'无扩展权限（ext字段需填空）',
        -13: u'IP校验错误',
        -14: u'内容解析异常',
        -24: u'手机号码超过限定个数',
        -25: u'没有提交权限',
        -990: u'未知错误'
    }

    actions = {
        '_send': {
            'url': 'http://120.55.248.18/smsSend.do',
            'params': {
                'mobile': '',
                'content': '',
                'dstime': '',
                'ext': '',
                'msgid': '',
                'msgfmt': '',
            },
        },
        '_query_balance': {
            'url': 'http://120.55.248.18/balanceQuery.do',
            'params': {}
        }
    }

    def trans_response(self, resp, action_name):
        resp = resp.strip()
        code = int(resp)
        if code > 0:
            return True, code
        else:
            return False, self.STATUS_CODE.get(code, u"未知错误")

    def send(self, phones, msg):
        phones_list = []
        if hasattr(phones, '__iter__'):
            for phone in phones:
                phones_list.append(str(phone))
            phones_str = ','.join(phones_list)
        else:
            phones_str = str(phones)
        success, resp = self._send(mobile=phones_str, content=msg)
        return resp

    def check_balance(self):
        return self._query_balance()
