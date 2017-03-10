import resource
import sys
t = resource.getrusage(resource.RUSAGE_SELF)
print t


class Profile:
    pass
    

def _p(frame, event, func):
    pass

def _t(frame, event, arg):
    print frame, event, arg

import profile

def x():
    import operator
    operator.add(1, 2)

if __name__ == '__main__':
    profile.runctx('x()', globals(), locals())
