# coding=utf-8
#########
# 名称: 标签分发器:
# 作者: weidwonder
# 作用: 允许函数或类同名, 在调用的时候通过标签来进行区分
#########

class TagDuplicatedError(BaseException):
    """ 标签重复错误
    """
    def __init__(self, tag_name):
        super(TagDuplicatedError, self).__init__("Tag %s is duplicated." % tag_name)

class CantFindTagError(BaseException):
    """ 找不到标签错误
    """
    def __init__(self, sth_name, tag_name):
        super(CantFindTagError, self).__init__("Can't find the '%s' object's '%s' tag." % (sth_name, tag_name))


class TagProxy:
    """ 标签分发器
    """

    # 分为两级 顶级字典{对象名: 二级字典} 二级字典{tag: 真实对象}
    TAG_DICT = {}

    class __DEFAULT_TAG:
        """ 默认标签
        """

        def __repr__(self):
            return 'default version'

    @classmethod
    def tag(cls, tag_name=None):
        """ 代理获取
        :param tag_name: 标签名
        :return: 真实对象
        """
        tag_name = tag_name or cls.__DEFAULT_TAG
        try:
            return cls.TAG_DICT[cls.__name__][tag_name]
        except:
            raise CantFindTagError(cls.__name__, tag_name)

    @classmethod
    def add_proxy(cls, sth, tag_name):
        """ 创建源对象的代理, 返回代理类
        :param sth: 源对象
        :param tag_name: 标签
        :return: 代理类
        """
        tag_name = tag_name or cls.__DEFAULT_TAG
        name = sth.__name__
        proxy = globals().get(name) or type(name, (TagProxy, object), {})
        sth_tag_dict = proxy.TAG_DICT.setdefault(name, {})
        if sth_tag_dict.has_key(tag_name):
            raise TagDuplicatedError(tag_name)
        else:
            sth_tag_dict[tag_name] = sth
        return proxy

    @classmethod
    def get_tags(cls, sth):
        name = sth.__name__
        proxy = globals().get(name) or type(name, (TagProxy, object), {})
        return proxy.TAG_DICT.keys()
    
    def __repr__(self):
        return ('< TagProxy for "%s" with tags:(%s) >' 
                % (self.__name__, ', '.join(self.get_tags(self.__name__))))


def tag(tag_name=None):
    """ tag 装饰器, 用来装饰类或函数
    :param tag_name: 标签名称(必须可哈希)
    :return: 指定标签装饰器
    """
    def tagged(sth):
        """ 指定标签的装饰器, 装饰一个类或函数, 返回分发器
        :param sth: 被装饰对象
        :return: 与对象同名标签分发器
        """
        proxy = TagProxy.add_proxy(sth, tag_name)
        return proxy
    return tagged


if __name__ == '__main__':

    @tag(1)
    def a():
        print 1
    @tag(2)
    def a():
        print 2

    @tag()
    def b():
        print 'b1'

    @tag(2)
    def b():
        print 'b2'


    b.tag()()
    a.tag(1)()
