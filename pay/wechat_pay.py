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

    def __init__(self, app_id, mch_id, dealer_key, cert_key, notify_url='', device_info='WEB', trade_type='APP'):
        """ 创建支付实例
        :param str app_id: 微信开放平台审核通过的应用APPID
        :param str mch_id: 微信支付分配的商户号
        :param str dealer_key: 微信支付商户证书
        :param tuple cert_key: 证书秘钥路径数组
        :param str notify_url: 回调url
        :param str device_info: 终端设备号(门店号或收银设备ID)，默认请传"WEB"
        :param str trade_type: 交易类型, 默认APP交易
        """
        self.app_id = app_id
        self.mch_id = mch_id
        self.dealer_key = dealer_key
        self.notify_url = notify_url
        self.device_info = device_info
        if cert_key:
            if isinstance(cert_key, (tuple, list)) and len(cert_key) == 2 and isinstance(cert_key[0], basestring) and isinstance(cert_key[1], basestring):
                self.cert_key = cert_key
            elif isinstance(cert_key, basestring):
                self.cert_key = cert_key
            else:
                raise ValueError(u'cert_key必须是[证书路径, 密钥路径]数组')
        else:
            self.cert_key = None
        self.trade_type = trade_type

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
        :param float total_fee: 总价格(分为单位)
        :param str ip_address: ip地址
        :param str body: 请求描述
        :return dict: 返回微信端返回的所有信息
        """
        total_fee = str(int(total_fee))
        nonce_str = self.__make_random_nonce()
        request_params = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': nonce_str,
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
            'noncestr': nonce_str,
            'package': context.get('package'),
            'timestamp': context.get('timestamp'),
            'prepayid': context.get('prepay_id'),
            'partnerid': self.mch_id,
        }
        sign = self.__make_sign(**sign_regenerate_dict)
        context.update(sign=sign)
        wechat_context = {
            'weixin_msg': context,
            'nonce_str': nonce_str,
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
        xml_params = self.__prepare_query_params(**request_params)
        res = requests.post(self.WE_CHAT_ORDER_QUERY_URL, data=xml_params, headers={'Content-Type': 'text/xml'})
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
    
    def order_refund(self, out_trade_no, out_refund_no, total_fee, refund_fee):
        """　退款服务
        :param out_trade_no: 我方订单号
        :param out_refund_no: 我方退款号
        :param total_fee: 总交易数额
        :param refund_fee: 退款数额
        :return: 微信回执字典
        成功返回示例:
            {
              "cash_refund_fee": "1", 
              "coupon_refund_fee": "0", 
              "cash_fee": "1", 
              "refund_id": "2006082001201612060629857889", 
              "coupon_refund_count": "0", 
              "refund_channel": "None", 
              "nonce_str": "Y858bSXiLfSW***d", 
              "return_code": "SUCCESS", 
              "return_msg": "OK", 
              "sign": "628CDC94553C8F891B82AD55D***BDE6", 
              "mch_id": "126*****01", 
              "out_trade_no": "20161206140650093***0350", 
              "transaction_id": "40060820012016120***59406202", 
              "total_fee": "1", 
              "appid": "wx63ff0f6*****7913", 
              "out_refund_no": "2016****93311", 
              "refund_fee": "1", 
              "result_code": "SUCCESS"
            }
        失败返回示例:
            {
              "nonce_str": "NOIQGN4Tsan***gn", 
              "return_code": "SUCCESS", 
              "return_msg": "OK", 
              "sign": "811C1C4BF9B72***47F121AF21C3C91B", 
              "mch_id": "126*****01", 
              "err_code_des": "订单状态错误", 
              "appid": "wx63ff0f6*****7913", 
              "result_code": "FAIL", 
              "err_code": "TRADE_STATE_ERROR"
            }
        """
        nonce_str = self.__make_random_nonce()
        request_params = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': nonce_str,
            'out_trade_no': out_trade_no,
            'out_refund_no': out_refund_no,
            'total_fee': total_fee,
            'refund_fee': refund_fee,
            'op_user_id': self.mch_id,
        }
        xml_params = self.__prepare_query_params(**request_params)
        res = requests.post(self.REFUND_URL, data=xml_params, cert=self.cert_key,
                            headers={'Content-Type': 'text/xml'}, verify=True)
        context = self.__parse_xml_result(res.content)
        return context