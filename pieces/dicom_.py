# coding=utf-8


def get_tag_value(ds, tag_a, tag_b, default=None):
    """
    获取dataset
    :param ds: Dataset 待获取对象dataset
    :param tag_a: int 第一级tag十六进制数
    :param tag_b: int 第二级tag十六进制数
    :param default: object 缺省返回
    :return: object
    """
    val = ds.get((tag_a, tag_b), default=default)
    if hasattr(val, 'value'):
        return val.value
    else:
        return val
