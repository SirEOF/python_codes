# coding=utf-8
from UserDict import UserDict


def reverse_dict(odict):
    """ 简单翻转键值
    """
    return dict(map(lambda t: (t[1], t[0]), odict.iteritems()))


def list_reverse_dict(odict):
    """ 翻转字典键值, 所有的值都是列表, 以应对重复键.
    """
    tdict = {}
    for k, v in odict.iteritems():
        new_v = tdict.get(v, [])
        new_v.append(k)
        tdict[v] = new_v
    return tdict


def list_restore_dict(odict):
    """ 将被翻转的键值还原
    """
    tdict = {}
    for k, v in odict.iteritems():
        for new_k in v:
            tdict[new_k] = k
    return tdict


def clean_dict(kws, judge=bool):
    for k, v in kws.items():
        if not judge(v):
            kws.pop(k)
    return kws


def clean_dict_by_key(kws):
    for k, v in kws.items():
        if not k:
            kws.pop(k)
    return kws


class OnlyDict(dict):
    """
    包含一个默认值的字典
    """

    def __init__(self, default_val, *args, **kws):
        self._default_val = default_val
        super(OnlyDict, self).__init__(*args, **kws)

    def __getitem__(self, item):
        return self.get(item, None) or self._default_val


class OnlyObject(object):
    """
    包含默认属性的对象, 如果获取一个不存在的属性, 则返回默认值
    """

    def __init__(self, default_val, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._default_val = default_val

    def __getattr__(self, item):
        return self._default_val


class DictObject(object):
    """ 转化字典键值到对象属性
    """

    def __init__(self, entries, has_default=False, default=None):
        self.__dict__.update(**entries)
        self.__has_default = has_default
        self.__default = default

    def __getattr__(self, item):
        if self.__has_default:
            return self.__default
        else:
            raise AttributeError("'{name}' object has no attribute '{item}'".format(name=self.__class__.__name__, item=item))

    def __setattr__(self, key, value):
        self.__dict__[key] = value


class NoneDuplicatedDict(UserDict):
    """ 值无重名字典
    """

    def __init__(self, *args, **kws):
        UserDict.__init__(self, *args, **kws)
        _reverse_dict = reverse_dict(self)
        assert len(_reverse_dict) != len(self)


class NoneDuplicatedObjectConstructor(type):
    """ 不允许属性的值重复
    """

    def __new__(mcs, name, bases, attrs):
        def get_fields(cls):
            """ 获取用户定义的公有属性
            """
            fields = {k: v for k, v in cls.__dict__.items() if not (k.startswith('__') and k.endswith('__'))}
            return fields

        # 将所有属性是以NoneDuplicatedObjectConstructor为元类的对象属性全部提取到顶层
        handle_queue = list(attrs.items())
        new_attrs = []
        while handle_queue:
            k, v = handle_queue.pop()
            if k.startswith('__'):
                continue
            if isinstance(v, mcs):
                handle_queue.extend(get_fields(v).items())
            else:
                new_attrs.append((k, v))
        attrs_reverse = [(v, k) for k, v in new_attrs]
        assert len(new_attrs) == len(dict(attrs_reverse)), "类%s内部存在重复值" % name
        attrs['__all_vals'] = [i[1] for i in new_attrs]
        attrs['__choices'] = attrs_reverse
        return super(NoneDuplicatedObjectConstructor, mcs).__new__(mcs, name, bases, attrs)


class NoneDuplicatedObject(object):
    """ 属性值不可重复字典, 同样会遍历其属性中的NoneDuplicatedObject实例
    """
    __metaclass__ = NoneDuplicatedObjectConstructor

    @classmethod
    def get_values(cls):
        """ 获取用户定义的公有属性
        """
        return cls.__dict__['__all_vals']

    @classmethod
    def choices(cls):
        """ 获取选项 
        """
        return cls.__dict__['__choices']
