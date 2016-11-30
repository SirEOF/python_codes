# -*- coding: utf-8 -*-
import hashlib
import random
import time
import xml.etree.ElementTree as ElementTree
from datetime import datetime
from operator import itemgetter

import requests
from django.utils.encoding import smart_str, smart_unicode
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class WeChatPay(object):
    """ 微信支付
    文档地址: https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_1
    """

    # 申请订单URL
    WE_CHAT_PAY_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    WE_CHAT_ORDER_QUERY_URL = 'https://api.mch.weixin.qq.com/pay/orderquery'
    REFUND_URL = 'https://api.mch.weixin.qq.com/secapi/pay/refund'

    def __init__(self, app_id, mch_id, dealer_key, notify_url='', device_info='WEB'):
        """ 创建支付实例
        :param str app_id: 微信开放平台审核通过的应用APPID
        :param str mch_id: 微信支付分配的商户号
        :param str dealer_key: 微信支付商户证书
        :param str notify_url: 回调url
        :param str device_info: 终端设备号(门店号或收银设备ID)，默认请传"WEB"
        """
        self.app_id = app_id
        self.mch_id = mch_id
        self.dealer_key = dealer_key
        self.notify_url = notify_url
        self.device_info = device_info

        self.trade_type = 'APP'

    def __prepare_query_params(self, **kwargs):
        """ 准备请求参数
        :param dict kwargs: 参数字典 
        :return dict:
        """
        rtn_params = kwargs.copy()
        sign = self.__make_sign(**kwargs)
        rtn_params.update(sign=sign)
        xml_params = self.__make_xml_params(**rtn_params)
        return xml_params

    def __make_sign(self, **items):
        """ 按规则生成签名
        :param dict items: 参数键值对
        :return unicode: sign 签名
        """
        items = items.copy().items()
        items.sort(key=itemgetter(0))
        items.append((u'key', self.dealer_key))
        sign_peers = [u'{k}={v}'.format(k=k, v=v) for k, v in items if v]
        peers_str = u'&'.join(sign_peers)
        sign_key = hashlib.md5(peers_str).hexdigest().upper()
        sign_key = sign_key
        return sign_key

    @staticmethod
    def __make_random_nonce():
        """ 生成随机数算法
        :return str: 随机数
        """
        time_str = datetime.now().strftime('%Y%m%d%H%M%S%f')
        random_num = str(random.randrange(0, 1e4)).rjust(4, '0')
        nonce_str = hashlib.md5(time_str + random_num).hexdigest().upper()
        return nonce_str

    @staticmethod
    def __make_xml_params(**kwargs):
        """ 根据参数生成XML文件
        :param dict kwargs:
        :return str: 请求参数的XML字符串.
        """
        xml_items = ['\t<{k}>{v}</{k}>\n'.format(k=k, v=v) for k, v in kwargs.items() if v]
        xml_str = '<xml>\n{xml_items}</xml>'.format(xml_items=''.join(xml_items))
        return xml_str

    @staticmethod
    def __parse_xml_result(content):
        """ 解析 XML 数据
        :param str content: XML 数据
        :return dict: XML tag:内容 相对应的 key-val 键值对字典.
        """
        result = {}
        if not content:
            return result
        raw_str = smart_str(content)
        root_elem = ElementTree.fromstring(raw_str)
        if root_elem.tag == 'xml':
            for child in root_elem:
                result[child.tag] = smart_unicode(child.text)
        return result

    def gen_order(self, trade_no, total_fee, ip_address, body='', notify_url=''):
        """ 请求生成支付订单
        :param str trade_no: 订单号
        :param int total_fee: 总价格(分为单位)
        :param str ip_address: ip地址
        :param str body: 请求描述
        :return dict: 返回微信端返回的所有信息
        """
        self.nonce_str = self.__make_random_nonce()
        request_params = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': self.nonce_str,
            'body': body,
            'out_trade_no': trade_no,
            'total_fee': total_fee,
            'spbill_create_ip': ip_address,
            'notify_url': notify_url or self.notify_url,
            'trade_type': self.trade_type,
        }
        xml_params = self.__prepare_query_params(**request_params)
        res = requests.post(self.WE_CHAT_PAY_URL, data=xml_params,
                            headers={'Content-Type': 'text/xml'}, verify=False)
        context = self.__parse_xml_result(res.content)
        context.update({
            'timestamp': int(time.time()),
            'package': 'Sign=WXPay',
            'partnerid': self.mch_id,
        })

        # 服务端在接收到微信返回的结果后，需要重新生成 sign
        sign_regenerate_dict = {
            # sign 需要重新生成
            'appid': self.app_id,
            'noncestr': self.nonce_str,
            'package': context.get('package'),
            'timestamp': context.get('timestamp'),
            'prepayid': context.get('prepay_id'),
            'partnerid': self.mch_id,
        }
        sign = self.__make_sign(**sign_regenerate_dict)
        context.update(sign=sign)
        wechat_context = {
            'weixin_msg': context,
            'nonce_str': self.nonce_str,
            'trade_no': trade_no,
            'prepay_id': context.get('prepay_id')
        }
        return wechat_context

    def get_pay_order_query(self, trade_no):
        """ 查询订单结果
        :param str trade_no: 订单号
        :return dict: 返回微信端查询返回的信息
        """
        request_params = {
            'appid': self.app_id,
            'mch_id': self.mch_id or self.mch_id,
            'out_trade_no': trade_no,
            'nonce_str': self.__make_random_nonce(),
        }
        self.__prepare_query_params(**request_params)
        res = requests.post(self.WE_CHAT_ORDER_QUERY_URL, data=self.xml_params, headers={'Content-Type': 'text/xml'})
        context = self.__parse_xml_result(res.content)
        return context

    def verify_sign(self, **kwargs):
        """ 验证微信返回过来的 sign 字段是否正确
        :param dict kwargs: 返回的所有字段
        :return bool: 验证是否通过 
        """
        sign = kwargs.pop('sign', None)
        real_sign = self.__make_sign(**kwargs)
        return real_sign == sign

    def gen_notify_resp(self, success, message='ok'):
        """ 生成回调回复
        :param bool success: 是否成功
        :param str message: 信息内容
        :return str: 回复给微信的结构体
        """
        status_str = 'SUCCESS' if success else 'FAIL'
        return (u'<return_code><![CDATA[{status}]]></return_code>'
                u'<return_msg><![CDATA[{message}]]></return_msg>').format(status=status_str, message=message)

    xml2dict = __parse_xml_result