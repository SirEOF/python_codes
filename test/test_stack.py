import inspect
import operator

from async_iter import AsyncIterHandler

from django_tools.serializer import jprint, to_json

multitasking = AsyncIterHandler('threading')


def print_stack():
    jprint(map(operator.itemgetter(3), inspect.stack()))


class C(object):
    """ haha
    """

    x = y = 1

    _g = 2

    @property
    def g(self):
        return 1


lines = inspect.getsourcelines(C)
print to_json(lines[0])


def getdefinedattrs(object):
    """ get class attrs list

    Return attrs are defined in class despite whether those attrs 
    are inherited from bases or not.
    """
    if not inspect.isclass(object):
        raise TypeError('{!r} is not a class'.format(object))
    lines = inspect.getsourcelines(C)
    return ''
