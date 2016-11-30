# coding=utf-8
import datetime
import random


class OrderUtil(object):
    """ 订单工具类
    """

    @classmethod
    def gen_order_no(cls):
        """ 生成订单号
        :return str: 订单号
        """
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + str(random.randrange(0, 1e4)).rjust(4, '0')
