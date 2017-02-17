import datetime as dt
import inspect
from collections import defaultdict
from functools import wraps

import operator
import types
from django.views.generic import View

tree = defaultdict(lambda : timing_dict)

timing_dict = tree

running_stack = []
running_sets = set()

def timing(func):
    @wraps(func)
    def wrap_func(*args, **kws):
        fn = func.__name__
        start = dt.datetime.now()
        func_stack = map(operator.itemgetter(3), inspect.stack())
        running_stack.append(fn)
        running_sets.add()
        rtn = func(*args, **kws)
        end = dt.datetime.now()
        time_cost = end - start
        timing_dict.setdefault(fn, {'times': 0, 'time_costs': [], 'params': [], 'total_costs': dt.timedelta(0)})
        timing_dict[fn]['times'] += 1
        timing_dict[fn]['time_costs'].append(time_cost)
        timing_dict[fn]['params'].append((args, kws))
        timing_dict[fn]['total_costs'] += time_cost
        return rtn

    return wrap_func


def show_timing_cost(detail=False):
    func_cost_tuples = sorted(timing_dict.items(), key=lambda _: _[1]['total_costs'], reverse=True)
    total_cost = sum([_[1]['total_costs'].total_seconds() for _ in func_cost_tuples])
    print '%(func)-30s:%(total_secs)-12s%(call_times)-12s%(percent)s' % dict(func=u'method_name', total_secs=u'total_cost', 
                                                                            call_times=u'times_run', percent=u'percent')
    for k, v in func_cost_tuples:
        total_seconds = v['total_costs'].total_seconds()
        percent = round(total_seconds / total_cost * 100, 2)
        print '%(func)-30s:%(total_secs)-12s%(call_times)-12s%(percent)s' % dict(func=k, total_secs=total_seconds, 
                                                                                call_times=v['times'], percent=percent)
        if detail:
            for i, time_cost in enumerate(v['time_costs']):
                params = v['params'][i]
                params_str = ', '.join([str(_) for _ in params[0]]) + ', ' + ', '.join(
                    [str(k) + '=' + repr(v) for k, v in params[1]])
                print '\t - %(time_cost)s\t -%(params)s' % dict(time_cost=time_cost.total_seconds(), params=params_str)


def view_timing(view):
    for attr_name in set(dir(view)) - set(dir(View)):
        attr = getattr(view, attr_name)
        if isinstance(attr, types.MethodType):
            setattr(view, attr_name, timing(attr))
    return view
