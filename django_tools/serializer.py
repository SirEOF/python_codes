# coding=utf-8
import datetime
import decimal
import json
import time

import uuid
from django.core.serializers.json import DjangoJSONEncoder


def datetime2timestamp(datetime_obj):
    """ datetime类型到时间戳(毫秒)
    :param datetime_obj: datetime对象
    :return int: 微秒时间戳
    """
    return int(time.mktime(datetime_obj.timetuple()) * 1000)


def standardized_model(obj, fields=None, exclude=None, foreign_fields=None):
    """ 对model对象进行序列化
    :param Model obj: 待序列化对象
    :param fields: 指定输出的字段 
    :param exclude: 指定刨除的字段
    :param foreign_fields: 加载的外键字段
    :return dict: 序列化后的字典
    """
    if not exclude:
        exclude = []
    if not foreign_fields:
        foreign_fields = []
    if not obj:
        return {}
    context = {}
    if fields:
        field_names = fields
    else:
        field_names = [f.attname for f in obj._meta.fields]
    for f in exclude:
        field_names.remove(f)
    field_names.extend([f for f in foreign_fields if f not in field_names])
    for field_name in field_names:
        field_val = getattr(obj, field_name)
        context[field_name] = field_val
    return context


def standardized_queryset(queryset):
    """ 对queryset进行序列化
    :param QuerySet queryset: 待序列化queryset
    :return: 序列化后的内容
    """
    rtn_list = []
    for o in queryset:
        if isinstance(o, dict):
            rtn_list.append(o)
        else:
            rtn_list.append(standardized_model(o))
    return rtn_list


class JSONEncoder(DjangoJSONEncoder):
    """ JSON序列化编码类
    增加对django orm序列化的支持
    """

    def default(self, o):
        from django.db import models
        if isinstance(o, models.Model):
            return standardized_model(o)
        elif isinstance(o, models.query.QuerySet):
            return standardized_queryset(o)
        elif isinstance(o, decimal.Decimal):
            return round(float(o), 6)
        if isinstance(o, datetime.datetime):
            datetime2timestamp(o)
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        else:
            try:
                return super(DjangoJSONEncoder, self).default(o)
            except TypeError:
                return repr(o)


def to_json(obj):
    """ 将对象转化为json
    :param obj: 待转化对象
    :return string: 转化后的json字符串
    """
    return json.dumps(obj, indent=2, ensure_ascii=False, cls=JSONEncoder)


def jprint(obj):
    """ 打印obj序列化后的字符串
    """
    print to_json(obj)
