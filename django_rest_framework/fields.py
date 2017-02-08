# coding=utf-8
import time

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.relations import PKOnlyObject


class DateTimestampField(serializers.DateTimeField):
    """ 时间戳字段(毫秒)
    """

    def to_representation(self, datetime_obj):
        return int(time.mktime(datetime_obj.timetuple()) * 1000)


class ForeignKeyRelatedField(serializers.RelatedField):
    """ 可指定外键字段
    当读取时返回serializer格式， 添加时为其外键值
    """
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid pk "{pk_value}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.'),
    }

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', None)
        self.serializer_class = kwargs.pop('serializer_class', None)
        self.instance = None
        assert issubclass(self.serializer_class, serializers.ModelSerializer), \
                _('The argument `serializer_class` must be a subclass of ModelSerializer.')
        kwargs['queryset'] = kwargs.pop('queryset', self.serializer_class.Meta.model.objects)
        super(ForeignKeyRelatedField, self).__init__(**kwargs)

    def use_pk_only_optimization(self):
        return True

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        if isinstance(data, PKOnlyObject):
            data = data.pk
        try:
            self.instance = self.get_queryset().get(pk=data)
            return self.instance
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)

    def to_representation(self, value):
        value = self.instance or self.to_internal_value(value)
        return self.serializer_class(instance=value).data
