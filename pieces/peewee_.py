# coding=utf-8
import peewee


class PrimaryKeyField(peewee.BigIntegerField):
    db_field = 'primary_key'

    def __init__(self, *args, **kwargs):
        kwargs['primary_key'] = True
        super(PrimaryKeyField, self).__init__(*args, **kwargs)

    def __ddl__(self, column_type):
        ddl = super(PrimaryKeyField, self).__ddl__(column_type)
        return ddl + [peewee.SQL('auto_increment')]


def monkey_patch_peewee():
    """
    修正peewee不能正确支持Bigint主键的问题
    """
    peewee.PrimaryKeyField = PrimaryKeyField
