# coding=utf-8
import json

import requests


class XiaoMiApiException(Exception):
    """ 小米接口调用异常
    """
    pass


class XiaoMiOAuth(object):
    """ 微信APP登录后端Oauth SDK
    """

    placeholder = '&&&START&&&'

    def __init__(self, client_id, client_secret, redirect_uri):
        """
        :param str client_id: 应用id
        :param str client_secret: 应用secret
        :param str redirect_uri: 应用重定向url
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        super(XiaoMiOAuth, self).__init__()

    def get_access_token(self, code):
        """ 根据code获取access_token
        :param str code: 客户端从小米那里获取的获取access_token的串码
        :exception XiaoMiApiException:
        :return dict: 
            {
                "access_token": "access token value",
                "expires_in": 360000,
                "refresh_token": "refresh token value",
                "scope": "scope value",
                "token_type ": "mac",
                "mac_key ": "mac key value",
                "mac_algorithm": "HmacSha1",
                "openId":"2.0XXXXXXXXX"
            }
        """
        url = 'https://account.xiaomi.com/oauth2/token'
        try:
            resp = requests.get(url, params={
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
            }, verify=False)
            resp_content = resp.content.replace(self.placeholder, '')
            resp_dict = json.loads(resp_content)
        except Exception as e:
            raise XiaoMiApiException(u'小米api调用出错:' + e.message)
        if resp_dict.get('error'):
            raise XiaoMiApiException(resp_dict.get('error_description'))
        return resp_dict

    def refresh_access_token(self, refresh_token):
        """ 刷新access_token
        :param str refresh_token: access_token对应的refresh_token 
        :exception XiaoMiApiException:
        :return dict: 
            {
                "access_token": "access token value",
                "expires_in": 360000,
                "refresh_token": "refresh token value",
                "scope": "scope value",
                "token_type ": "mac",
                "mac_key ": "mac key value",
                "mac_algorithm": " HmacSha1",
                "openId":"2.0XXXXXXXXX"
            }
        """
        url = 'https://account.xiaomi.com/oauth2/token'
        try:
            resp = requests.get(url, params={
                'client_id': self.client_id,
                'redirect_uri': '',  # TODO
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }, verify=False)
            resp_content = resp.content.replace(self.placeholder, '')
            resp_dict = json.loads(resp_content)
        except Exception as e:
            raise XiaoMiApiException(u'小米api调用出错:' + e.message)
        if resp_dict.get('error'):
            raise XiaoMiApiException(resp_dict.get('error_description'))
        return resp_dict

    def get_user_info(self, access_token):
        """ 获取用户信息
        :param str access_token: 调用凭证
        :return dict: 
            {
                "miliaoNick": "小米帐号昵称",
                "userId": "小米用户账号",
                "miliaoIcon": "头像URL(会返回多个分辨率版本的头像)"
            }
        """
        url = 'https://open.account.xiaomi.com/user/profile'
        try:
            resp = requests.get(url, params={
                'clientId': self.client_id,
                'token': access_token,
            }, verify=False)
            resp_content = resp.content.replace(self.placeholder, '')
            resp_dict = json.loads(resp_content)
        except Exception as e:
            raise XiaoMiApiException(u'小米api调用出错:' + e.message)
        if resp_dict.get('result') != 'ok':
            raise XiaoMiApiException(resp_dict.get('description'))
        return resp_dict['data']

    def get_user_open_id(self, access_token):
        """ 获取用户open_id
        :param str access_token: 调用凭证
        :return str: open_id 
            }
        """
        url = 'https://open.account.xiaomi.com/user/openidV2'
        try:
            resp = requests.get(url, params={
                'client_id': self.client_id,
                'token': access_token,
            }, verify=False)
            resp_content = resp.content.replace(self.placeholder, '')
            resp_dict = json.loads(resp_content)
        except Exception as e:
            raise XiaoMiApiException(u'小米api调用出错:' + e.message)
        if resp_dict.get('result') != 'ok':
            raise XiaoMiApiException(resp_dict.get('description'))
        return resp_dict['data']['openid']

    def get_user_phone_email(self, access_token):
        """ 获取用户的手机号和邮箱
        :param access_token: 调用凭证
        :return dict:
            {
                "phone": "用户手机号，没有phone返回空",
                "email": "用户email, 没有email返回空"
            }
        """
        url = 'https://open.account.xiaomi.com/user/phoneAndEmail'
        try:
            resp = requests.get(url, params={
                'clientId': self.client_id,
                'token': access_token,
            }, verify=False)
            resp_content = resp.content.replace(self.placeholder, '')
            resp_dict = json.loads(resp_content)
        except Exception as e:
            raise XiaoMiApiException(u'小米api调用出错:' + e.message)
        if resp_dict.get('result') != 'ok':
            raise XiaoMiApiException(resp_dict.get('description'))
        return resp_dict['data']
