import inspect

from costom_profiling import show_timing_cost, activate_timing, install_importer
from django_tools.serializer import jprint

install_importer('..')

from async_iter import AsyncIterHandler

multitasking = AsyncIterHandler('threading')


def chain(inst):
    return inst.g()


class C(object):
    """ haha
    """

    x = y = 1

    def g(self):
        jprint(inspect.stack())
        self.h()

    def f(self):
        for i in range(3):
            chain(self)
        multitasking([(chain, (self,))] * 3)

    @classmethod
    def h(cls):
        print 'haha'

    @staticmethod
    def x():
        print 'heihei'


c = C()

activate_timing(locals())

c.f()
show_timing_cost()
