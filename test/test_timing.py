import inspect


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

    @classmethod
    def h(cls):
        pass

    @staticmethod
    def x():
        pass


c = C()

c.f()
