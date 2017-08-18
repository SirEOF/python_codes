# coding=utf-8
from __future__ import unicode_literals
from django.db import models


class DeletableManager(models.Manager):
    """
    可删除Manager
    """

    def get_queryset(self):
        return super(DeletableManager, self).get_queryset().filter(delete_flag=False)
