# coding=utf-8
"""
**Attention**
Because all members can be fetched from MemberRegistry, you don't need to import them.
But here comes with a problem, if the member is imported from nowhere, it won't be able to
register in MemberRegistry. So you must import it manually.
"""


class MemberNameConflictError(Exception):
    pass


class MemberNotExistsError(Exception):
    pass


class LazyMemberProxy(object):
    """
    Take a name to represent a member.
    It won't load the real member until the specific member method has been called.
    """

    __slots__ = ('__member', '__member_name')

    def __init__(self, member_name):
        self.__member_name = member_name
        self.__member = None

    def __getattr__(self, item):
        if not self.__member:
            try:
                self.__member = MemberRegistry.members[self.__member_name]
            except KeyError:
                raise MemberNotExistsError(u'member %s not exists.' % self.__member_name)
        return getattr(self.__member, item)


class MemberRegistry(object):
    """ all member inherit from BaseMember will be registered in here.
    you can fetch any member by calling `get_member` in anywhere.
    """
    __slots__ = ('__members',)

    members = {}

    @classmethod
    def get_member(cls, member_name):
        """ get a member from MemberRegistry
        return a LazyMemberProxy to prevent `loop import`.
        :param member_name: member class name
        :return LazyMemberProxy: a proxy represent the member.
        """
        return LazyMemberProxy(member_name)

    @classmethod
    def register(cls, member_name, member_cls):
        """ register a member class
        :param member_name: member's name
        :param member_cls: real member class
        """
        if member_name in cls.members:
            raise MemberNameConflictError(u'%s member name has conflicted.' % member_name)
        cls.members[member_name] = member_cls()

    def __init__(self):
        raise ValueError(u'MemberRegistry can\'t be instantiate.')


class MemberMeta(type):
    """ BaseMember's Meta
    """

    def __new__(mcs, name, bases, attrs):
        """ register every class inherit from BaseMember to MemberRegistry
        :param name: class name
        :param bases: class bases
        :param attrs: class attributes
        :return: real member class
        """
        cls = super(MemberMeta, mcs).__new__(mcs, name, bases, attrs)
        MemberRegistry.register(name, cls)
        return cls


class BaseMember(object):
    """ Basic member class
    """

    __metaclass__ = MemberMeta
