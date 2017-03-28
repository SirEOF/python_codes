# coding=utf-8
import requests


class WechatApiException(Exception):
    """ 微信接口调用异常
    """
    pass


class WechatOAuth(object):
    """ 微信APP登录后端Oauth SDK
    """

    def __init__(self, app_id, app_secret):
        """
        :param str app_id: 应用id
        :param str app_secret: 应用secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        super(WechatOAuth, self).__init__()

    def get_access_token(self, code):
        """ 根据code获取access_token
        :param str code: 客户端从微信那里获取的获取access_token的串码
        :exception WechatApiException:
        :return dict: 
            { 
                "access_token":"ACCESS_TOKEN", # 接口调用凭证
                "expires_in":7200, # 接口调用凭证超时时间，单位（秒）
                "refresh_token":"REFRESH_TOKEN",  # 用户刷新access_token
                "openid":"OPENID",  # 授权用户唯一标识
                "scope":"SCOPE",  # 用户授权的作用域，使用逗号（,）分隔
                "unionid":"o6_bmasdasdsad6_2sgVt7hMZOPfL",  # 当且仅当该移动应用已获得该用户的userinfo授权时，才会出现该字段
            }
        """
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        try:
            resp = requests.get(url, params={
                'appid': self.app_id,
                'secret': self.app_secret,
                'code': code,
                'grant_type': 'authorization_code',
            }, verify=False)
            resp.encoding = 'utf8'
            resp_dict = resp.json()
        except Exception as e:
            raise WechatApiException(u'微信api调用出错:' + e.message)
        if resp_dict.get('errcode'):
            raise WechatApiException(resp_dict.get('errmsg'))
        return resp_dict

    def refresh_access_token(self, refresh_token):
        """ 刷新access_token
        :param str refresh_token: access_token对应的refresh_token 
        :exception WechatApiException:
        :return dict: 
            { 
                "access_token":"ACCESS_TOKEN",  # 接口调用凭证
                "expires_in":7200,   # access_token接口调用凭证超时时间，单位（秒）
                "refresh_token":"REFRESH_TOKEN",  # 用户刷新access_token
                "openid":"OPENID",  # 授权用户唯一标识
                "scope":"SCOPE"  # 用户授权的作用域，使用逗号（,）分隔
            }
        """
        url = 'https://api.weixin.qq.com/sns/oauth2/refresh_token'
        try:
            resp = requests.get(url, params={
                'appid': self.app_id,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
            }, verify=False)
            resp.encoding = 'utf8'
            resp_dict = resp.json()
        except Exception as e:
            raise WechatApiException(u'微信api调用出错:' + e.message)
        if resp_dict.get('errcode'):
            raise WechatApiException(resp_dict.get('errmsg'))
        return resp_dict

    def get_user_info(self, access_token, openid):
        """ 获取用户信息
        :param str access_token: 调用凭证
        :param openid: 普通用户的标识，对当前开发者帐号唯一
        :return dict: 
            { 
                "openid":"OPENID",
                "nickname":"NICKNAME",
                "sex":1,
                "province":"PROVINCE",
                "city":"CITY",
                "country":"COUNTRY",
                "headimgurl": "http://wx.qlogo.cn/mmopen/g3Mo..bJxCfHe/0",
                "privilege":[
                    "PRIVILEGE1", 
                    "PRIVILEGE2"
                ],
                "unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"
            }
        """
        url = 'https://api.weixin.qq.com/sns/userinfo'
        try:
            resp = requests.get(url, params={
                'access_token': access_token,
                'openid': openid,
            }, verify=False)
            resp.encoding = 'utf8'
            resp_dict = resp.json()
        except Exception as e:
            raise WechatApiException(u'微信api调用出错:' + e.message)
        if resp_dict.get('errcode'):
            raise WechatApiException(resp_dict.get('errmsg'))
        return resp_dict
