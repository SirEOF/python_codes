# coding=utf-8
# 注意, 这里的服务可以直接从ServiceRegistry中获取, 这也带来一个问题,
# 就是所有的服务类都必须保证被引用到项目中

from django.core.exceptions import ObjectDoesNotExist


class ServiceNameConflictError(Exception):
    """ 服务名冲突异常
    """
    pass


class ServiceNotExistsError(Exception):
    """ 服务不存在异常
    """
    pass


class LazyServiceProxy(object):
    """ 懒惰服务代理
    用到这个服务的时候才加载
    """

    __slots__ = ('__service', '__service_name')

    def __init__(self, service_name):
        self.__service_name = service_name
        self.__service = None

    def __getattr__(self, item):
        if not self.__service:
            try:
                self.__service = ServiceRegistry._services[self.__service_name]
            except KeyError:
                raise ServiceNotExistsError(u'service %s not exists.' % self.__service_name)
        return getattr(self.__service, item)


class ServiceRegistry(object):
    """ 服务注册中心
    """
    __slots__ = ('__services',)

    _services = {}

    @classmethod
    def get_service(cls, service_name):
        """ 获取服务
        返回一个服务的代理, 防止加载期间相互依赖导致的找不到的问题
        :param service_name: 服务名
        :return LazyServiceProxy: 服务代理
        """
        return LazyServiceProxy(service_name)

    @classmethod
    def register(cls, service_name, service_cls):
        """ 注册服务
        :param service_name: 服务名
        :param service_cls: 服务类
        """
        if service_name in cls._services:
            raise ServiceNameConflictError(u'%s service name has conflicted.' % service_name)
        cls._services[service_name] = service_cls()

    def __init__(self):
        raise ValueError(u'ServiceRegistry can\'t be instantiate.')


class ServiceMeta(type):
    """ BaseService的服务元类
    """

    def __new__(mcs, name, bases, attrs):
        """ 将继承BaseService的服务都加入到服务注册机里边去
        :param name: 服务名
        :param bases: 服务基类, 一般都是BaseService
        :param attrs: 服务类属性
        :return: 服务类
        """
        cls = super(ServiceMeta, mcs).__new__(mcs, name, bases, attrs)
        ServiceRegistry.register(name, cls)
        return cls


class BaseService(object):
    """ 基本法服务类
    """

    __metaclass__ = ServiceMeta

    def get(self, *slug):
        """ 根据逻辑主键寻找指定的对象
        :param slug: 逻辑主键的值
        :return: Model / None
        """
        pass

    def _get(self, manager, query):
        """ 获取指定的对象
        :param manager: queryset_manager
        :param query: 查询对象
        :return: Model / None
        """
        try:
            m = manager.get(query)
        except ObjectDoesNotExist:
            return None
        return m

    def _get_queryset(self, manager, query):
        """ 获取对象queryset
        :param manager: queryset_manager
        :param query: 查询对象
        :return: Queryset
        """
        return manager.filter(query)