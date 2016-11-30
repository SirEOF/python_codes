# -*- coding: utf-8 -*-
import base64
import urllib

import requests
import rsa
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from datetime import datetime


class AliPay(object):
    """
    支付宝支付服务
    """

    GATE_WAY = 'https://mapi.alipay.com/gateway.do'

    class RefundElement(object):
        """ 退款单个元素
        """

        def __init__(self, ali_trade_no, refund_amount, describe=''):
            self.ali_trade_no = ali_trade_no
            self.refund_amount = refund_amount
            self.describe = describe

        def __str__(self):
            return str(self.ali_trade_no) + '^' + str(self.refund_amount) + '^' + str(self.describe)

    def __init__(self, app_id, app_private_key, app_public_key, ali_public_key, input_charset='utf-8', notify_url='',
                 partner='',
                 seller_id='', sign_type='RSA'):
        """  初始化阿里支付客户端
        :param app_id: app_id
        :param app_private_key: app私钥
        :param app_public_key: app公钥
        :param ali_public_key: ali公钥
        :param input_charset: 请求编码类型 
        :param notify_url: 支付宝服务器主动通知商户服务器里指定的页面http/https路径。建议商户使用https
        :param partner: 卖家支付宝账号对应的支付宝唯一用户号(以2088开头的16位纯数字),订单支付金额将打入该账户,一个partner可以对应多个seller_id
        :param seller_id: 收款支付宝用户ID。 如果该值为空，则默认为商户签约账号对应的支付宝用户ID
        :param sign_type: 签名类型
        """
        self.app_id = app_id
        self.app_private_key = app_private_key
        self.app_public_key = app_public_key
        self.alipay_public_key = ali_public_key
        self.input_charset = input_charset
        self.notify_url = notify_url

        self.partner = partner
        self.seller_id = seller_id
        self.sign_type = sign_type

    def __dict2str(self, quotes=True, **kwargs):
        """ 将请求参数的键值对转换称string
        :param bool quotes: 是否需要加引号
        :param dict kwargs: 请求参数
        :return unicode: 转化后的字符串
        """
        keys = sorted(kwargs.keys())
        item_strings = []
        for key in keys:
            value = unicode(kwargs[key])
            if not value:
                continue
            if quotes:
                value = u'\"' + value + u'\"'
            item_string = key + u'=' + value
            item_strings.append(item_string)
        rtn_str = u'&'.join(item_strings)
        return rtn_str

    def __str2dict(self, param_str):
        """ 将客户端返回参数转化为字典
        :param str param_str: 待转化字符串
        :return dict: 转化后的字典
        """
        context = {}
        if not param_str:
            return context
        param_list = param_str.split("&")
        for param in param_list:
            key, value = param.split('=', 1)
            value = value.replace('"', '')
            context[key] = value
        return context

    def __filter_sign_params(self, **kwargs):
        """ 筛选sign相关的参数.取出sign, sign_type, 空值参数.
        :param dict kwargs: 字典参数
        :return dict: 过滤后的字典
        """
        kwargs.pop('sign_type', None)
        kwargs.pop('sign', None)
        return kwargs

    def __make_sign(self, sign_message):
        """ 生成 sign
        :param unicode sign_message: 待加密的信息
        :return unicode: 加密后的sign
        """
        key = RSA.importKey(self.app_private_key)
        h = SHA.new(sign_message)
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(h)
        sign = base64.b64encode(signature)
        return sign

    def __check_sign(self, message, sign):
        """ 校验自生成的自签名
        :param unicode message: 待验证信息
        :param unicode sign: 签名
        :return bool: 验证是否成功
        """
        key = RSA.importKey(self.app_public_key)
        h = SHA.new(message)
        verifier = PKCS1_v1_5.new(key)
        return verifier.verify(h, base64.b64decode(sign))

    def __get_sign(self, param_str):
        """ 获取订单的sign
        :param unicode param_str: 待生成sign的字符串
        :exception ValueError: sign错误
        """
        sign = self.__make_sign(param_str)
        if self.__check_sign(param_str, sign):
            return urllib.quote(sign.encode("utf-8"), safe='')
        else:
            raise ValueError("sign错误")

    def __resolve_alipay_params(self, **kwargs):
        """ 解析支付宝返回的参数
        :param dict kwargs: 支付宝验证的字典
        :return dict: 验证好的字典
        """
        response_params_dict = {}
        for key, val in kwargs.iteritems():
            if isinstance(val, list):
                val = val[0]
            response_params_dict[str(key).encode('utf-8')] = str(val).encode('utf-8')
        return response_params_dict

    def __verify_alipay_sign(self, message, sign):
        """ 验证支付宝的签名
        :param unicode message: 待验证信息
        :param unicode sign: 签名
        :return bool: 是否验证通过
        """
        sign = base64.b64decode(sign)
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(self.alipay_public_key)
        try:
            return rsa.verify(message, sign, pubkey)
        except:
            return False

    def __verify_source(self, notify_id):
        """ 验证是否是来自支付宝发来的通知
        :param str notify_id: 验证者id
        :return bool: 是否验证通过
        """
        params = {
            'service': 'notify_verify',
            'partner': self.partner,
            'notify_id': notify_id
        }
        res = requests.get(self.GATE_WAY, params=params, verify=False)
        return res.text == 'true'

    def __get_pay_params(self, out_trade_no, total_fee, subject='', body='', service='mobile.securitypay.pay', payment_type=1):
        """ 创建订单后返回客户端的参数
        :param str out_trade_no: 订单号
        :param int total_fee: 总价格
        :param str subject: 商品的标题/交易标题/订单标题/订单关键字等
        :param str body: 对一笔交易的具体描述信息。如果是多种商品，请将商品描述字符串累加传给body
        :param str service: 接口名称，固定为mobile.securitypay.pay
        :param str payment_type: 支付类型, 支付为固定值 "1" 
        :return dict: 返回给客户端的订单支付信息字典
        """
        param_dict = {
            'service': service,
            'partner': self.partner,
            '_input_charset': self.input_charset,
            'notify_url': self.notify_url,
            'out_trade_no': out_trade_no,
            'subject': subject,
            'payment_type': payment_type,
            'seller_id': self.seller_id,
            'total_fee': total_fee,
            'body': body
        }
        return param_dict

    def gen_order(self, out_trade_no, total_fee, subject='', body='', service='mobile.securitypay.pay', payment_type='1'):
        """ 生成支付宝订单参数
        :param out_trade_no: 订单号
        :param total_fee: 总价格(单位: 元)
        :param subject: 商品的标题/交易标题/订单标题/订单关键字等
        :param body: 对一笔交易的具体描述信息。如果是多种商品，请将商品描述字符串累加传给body
        :param service: 接口名称，固定为mobile.securitypay.pay
        :param payment_type: 支付类型, 支付为固定值 "1" 
        :return dict: 返回给客户端的订单支付信息字典
        """
        param_dict = self.__get_pay_params(out_trade_no, total_fee, subject, body, service, payment_type)
        param_str = self.__dict2str(quotes=True, **param_dict)
        sign = self.__get_sign(param_str)
        order_msg = {
            'partner': self.partner,
            'seller_id': self.seller_id,
            'out_trade_no': out_trade_no,
            'subject': subject,
            'body': body,
            'total_fee': total_fee,
            'notify_url': self.notify_url,
            'service': service,
            'payment_type': payment_type,
            '_input_charset': self.input_charset,
            'sign': sign,
            'sign_type': self.sign_type,
        }
        return order_msg

    def notify_handler(self, **kwargs):
        """ 异步回调处理器
        :param dict kwargs: 参数字典
        :return dict: 解析后的字典
        """
        payment_dict = self.__resolve_alipay_params(**kwargs)
        cleaned_payment_dict = self.__filter_sign_params(**payment_dict)
        if not self.__verify_source(cleaned_payment_dict.get('notify_id')):
            raise ValueError("来源不是支付宝/已更新完成")
        payment_str = self.__dict2str(quotes=False, **cleaned_payment_dict)
        sign = payment_dict.get('sign')
        if not self.__verify_alipay_sign(payment_str, sign):
            raise ValueError("支付宝签名有误")
        return payment_dict

    def callback_handler(self, param_str):
        """ 支付宝同步通知处理器
        :param str param_str: 参数字典
        :return bool, dict: 是否通过检验, 解析后的字典
        """
        params = self.__str2dict(param_str)
        param_dict = self.__resolve_alipay_params(**params)
        sign = param_dict.get('sign')
        self.__filter_sign_params(**param_dict)
        payment_str = self.__dict2str(quotes=True, **param_dict)
        return self.__verify_alipay_sign(payment_str, sign), param_dict

    def order_refund(self, out_trade_no, refund_amount, batch_no, refund_elements):
        """ 退订订单
        :param str out_trade_no: 待退款订单号
        :param refund_fee: 
        :return: 
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        detail_data = '#'.join(map(str, refund_elements))
        params = {
            'partner': self.partner,
            'service': 'refund_fastpay_by_platform_pwd',
            'seller_user_id': self.partner,
            '_input_charset': self.input_charset,
            'notify_url': self.notify_url,
            'refund_date': timestamp,
            'batch_no': batch_no,
            'batch_num': len(refund_elements),
            'detail_data': detail_data,
            'sign_type': self.sign_type,
        }
        tmp_params = self.__filter_sign_params(**params)
        param_str = self.__dict2str(quotes=False, **tmp_params)
        sign = self.__get_sign(param_str)
        params['sign'] = sign
        for k, v in params.items():
            print str(k) + ':' + str(v)
        # params['sign_type'] = self.sign_type
        # res = requests.get(self.GATE_WAY, params=params, verify=False)
        # rtn_dict = res.content
        # return rtn_dict
