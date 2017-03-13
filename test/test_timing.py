from async_iter import AsyncIterHandler

from costom_profiling.profiler import Profiling

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
        multitasking([(chain, (self, ))] * 3)

    @classmethod
    def h(cls):
        print 'h'

    @staticmethod
    def x():
        pass


c = C()

with Profiling('../..'):
    c.f()
