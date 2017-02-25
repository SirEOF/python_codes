import inspect
from UserDict import UserDict

from profiling import show_timing_cost, install_importer, activate_timing, timing

# install_importer('..')

from time import sleep

from async_iter import AsyncIterHandler


multitasking = AsyncIterHandler('threading')


def chain(inst):
    return inst.g()


class C(object):
    """ haha
    """

    x = y = 1

    def g(self):
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


print  C.h.__self__
print inspect.ismethod(C.h)
print inspect.ismethod(C.x)

activate_timing(locals())

c.f()
show_timing_cost()
