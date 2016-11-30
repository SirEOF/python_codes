# coding=utf-8
import math


class DistanceUtils:
    @staticmethod
    def fake_china_geo_cos(x):
        """ 针对中国的地理环境进行多项式拟合的cosine
        """
        return 5.028910732660628E-7 * (x * x * x) - 1.7587983610909379E-4 * (
            x * x) + 4.533824076804645E-4 * x + 0.997069708253254

    @classmethod
    def baidu_distance_simple(cls, lat_a, lng_a, lat_b, lng_b):
        """ 根据美团博客优化后的算法
        :param lat_a: a latitude
        :param lng_a: a longitude
        :param lat_b: b latitude
        :param lng_b: b longitude
        :return: distance between a and b (meter).
        """
        dx = float(lng_a) - float(lng_b)
        dy = float(lat_a) - float(lat_b)
        avg_lat = (float(lat_a) + float(lat_b)) / 2.0
        lx = cls.fake_china_geo_cos(avg_lat) * (dx / 180.0) * 3.14159265359 * 6367000.0
        ly = 6367000.0 * (dy / 180.0) * 3.14159265359
        return math.sqrt(lx * lx + ly * ly)
