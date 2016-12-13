# coding=utf-8

""" 环信聊天服务
"""
import json
import requests
from time import time, sleep
from UserDict import UserDict


class EasemobChat(object):
    """ 环信基本服务类
    """

    EASEMOB_HOST = 'https://a1.easemob.com'

    def __init__(self, setting, debug=False, error_handler=None):
        """ 
        :param object or dict setting: 设置
        :param bool debug: debug模式
        :param function error_handler: 处理错误函数
        :return: 
        """
        if isinstance(setting, (UserDict, dict)):
            self.CLIENT_ID = setting['CLIENT_ID']
            self.CLIENT_SECRET = setting['CLIENT_SECRET']
            self.ORG_NAME = setting['ORG_NAME']
            self.APP_NAME = setting['APP_NAME']
        else:
            self.CLIENT_ID = setting.CLIENT_ID
            self.CLIENT_SECRET = setting.CLIENT_SECRET
            self.ORG_NAME = setting.ORG_NAME
            self.APP_NAME = setting.APP_NAME
        self.DEBUG = debug
        self.ACCESS_TOKEN = None
        self.TOKEN_EXPIRED_TIME = 0
        self.APPLICATION = None
        self.error_handler = error_handler
        self._url_prefix = self.EASEMOB_HOST + "/%s/%s" % (self.ORG_NAME, self.APP_NAME)
        self.get_token()

    @property
    def _header(self):
        return {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.get_token()
        }

    def _post(self, url, data=None, **kws):
        r = requests.post(url, json=data, headers=self._header, timeout=3, **kws)
        return self._http_result(r)

    def _get(self, url, params=None):
        r = requests.get(url, params, headers=self._header, timeout=3)
        return self._http_result(r)

    def _delete(self, url):
        r = requests.delete(url, headers=self._header, timeout=3)
        return self._http_result(r)

    def _http_result(self, r):
        if self.DEBUG:
            error_log = {
                "method": r.request.method,
                "url": r.request.url,
                "request_header": dict(r.request.headers),
                "response_header": dict(r.headers),
                "response": r.text
            }
            if r.request.body:
                error_log["payload"] = r.request.body
            print json.dumps(error_log, ensure_ascii=False, indent=2)
        print r.status_code
        if r.status_code == requests.codes.ok:
            return True, r.json()
        else:
            return False, r.text

    def _get_token(self):
        """ 请求环信token
        """
        url = self._url_prefix + '/token'
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }
        success, r = self._http_result(requests.post(url, json=payload, headers={'content-type': 'application/json'}))
        if success:
            self.ACCESS_TOKEN = r['access_token']
            self.TOKEN_EXPIRED_TIME = time() + int(r['expires_in']) / 2
            self.APPLICATION = r['application']
            return True
        else:
            print r
            return False

    def get_token(self):
        """ 获取环信token
        """
        if time() > self.TOKEN_EXPIRED_TIME:
            token_flushed = False
            times = 0
            while not token_flushed and times <= 3:
                token_flushed = self._get_token()
                times += 1
                sleep(times)
            if not token_flushed and self.error_handler:
                self.error_handler(u'{app_name}获取token失败')
        return self.ACCESS_TOKEN

    def register_user(self, username, password):
        """ 注册单个用户
        :param str username: 用户名
        :param str password: 密码
        :return (bool, dict or string): 
        """
        params = {"username": username, "password": password}
        url = self._url_prefix + '/users'
        return self._post(url, params)

    def register_users(self, users):
        """ 注册多个用户
        :param list users: 用户字典列表
        :return (bool, dict or string): 
        """
        index = 0
        failed_list = []
        while index < len(users):
            to_register = users[index: index + 30]
            url = self._url_prefix + '/users'
            success, resp = self._post(url, to_register)
            if not success:
                failed_list.extend(to_register)
            sleep(0.05)
            index += 30
        return failed_list

    def get_user(self, username):
        """ 获取用户信息
        :param str username: 用户名
        :return (bool, dict or string): 
        """
        url = self._url_prefix + '/users/' + username
        success, resp = self._get(url)
        return success, resp

    def delete_user(self, username):
        """ 删除单个用户
        :param str username: 用户名
        :return (bool, dict or string): 
        """
        url = self._url_prefix + "/users/%s" % username
        return self._delete(url)
