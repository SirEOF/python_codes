from profiling import show_timing_cost, install_importer, activate_timing

install_importer('..')

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
        sleep(1)
        self.h()

    def f(self):
        for i in range(3):
            chain(self)
        multitasking([(chain, (self,))] * 3)

    def h(self):
        print 'haha'


c = C()

for n, a in locals().items():
    if n == 'install_importer':
        print a.__module__


activate_timing(locals())
c.f()
show_timing_cost()
