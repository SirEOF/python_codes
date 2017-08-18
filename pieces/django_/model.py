# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

from tools.django_.managers import DeletableManager


class Base(models.Model):
    """
    基本类
    """

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        abstract = True


class UpdatableBase(Base):
    """
    可更新类
    """

    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class SoftDeletableBase(UpdatableBase):
    """
    可删除类
    """
    delete_flag = models.BooleanField(default=False, verbose_name='删除标志')
    delete_time = models.DateTimeField(blank=True, null=True, verbose_name='删除时间')

    objects = DeletableManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.delete_time = now()
        self.delete_flag = True
        self.save(using=using)
