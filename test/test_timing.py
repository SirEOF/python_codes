from time import sleep

from async_iter import AsyncIterHandler

from profiling import view_timing, show_timing_cost

multitasking = AsyncIterHandler('threading')


def chain(inst):
    return inst.g()


@view_timing
class C(object):
    """ haha
    """

    x = y = 1

    def g(self):
        sleep(1)
        self.h()

    def f(self):
        for i in range(3):
            chain(self)
        multitasking([(chain, (self,))] * 3)

    def h(self):
        print 'haha'


c = C()
c.f()

show_timing_cost()
