import datetime as dt
import timeit
import types
from functools import wraps
from operator import itemgetter

from django.views.generic import View


class TimingManager(object):
    """Context Manager used with the statement 'with' to time some execution.

    Example:

    with TimingManager() as t:
       # Code to time
    """

    clock = timeit.default_timer

    def __enter__(self):
        """
        """
        self.start = self.clock()
        self.log('\n=> Start Timing: {}')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        """
        self.endlog()

        return False

    def log(self, s, elapsed=None):
        """Log current time and elapsed time if present.
        :param s: Text to display, use '{}' to format the text with
            the current time.
        :param elapsed: Elapsed time to display. Dafault: None, no display.
        """
        print s.format(self._secondsToStr(self.clock()))

        if (elapsed is not None):
            print 'Elapsed time: {}\n'.format(elapsed)

    def endlog(self):
        """Log time for the end of execution with elapsed time.
        """
        self.log('=> End Timing: {}', self.now())

    def now(self):
        """Return current elapsed time as hh:mm:ss string.
        :return: String.
        """
        return str(dt.timedelta(seconds=self.clock() - self.start))

    def _secondsToStr(self, sec):
        """Convert timestamp to h:mm:ss string.
        :param sec: Timestamp.
        """
        return str(dt.datetime.fromtimestamp(sec))


timing_dict = {}


def timing(func):
    @wraps(func)
    def wrap_func(*args, **kws):
        start = dt.datetime.now()
        rtn = func(*args, **kws)
        end = dt.datetime.now()
        time_cost = end - start
        timing_dict.setdefault(func.__name__, {'times': 0, 'time_costs': [], 'params': [], 'total_costs': dt.timedelta(0)})
        timing_dict[func.__name__]['times'] += 1
        timing_dict[func.__name__]['time_costs'].append(time_cost)
        timing_dict[func.__name__]['params'].append((args, kws))
        timing_dict[func.__name__]['total_costs'] += time_cost
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
