import inspect
import operator

from async_iter import AsyncIterHandler

from django_tools.serializer import jprint

multitasking = AsyncIterHandler('threading')

def print_stack():
    jprint(map(operator.itemgetter(3), inspect.stack()))

class C(object):
    def f(self):
        task_list = []
        for i in range(10):
            task_list.append((self.g,) )
        multitasking(task_list)

    def g(self):
        import threading
        print threading._active
        multitasking({
            '1': (print_stack, )
        })


    def write(self, obj):
        print obj


c = C()
c.f()
