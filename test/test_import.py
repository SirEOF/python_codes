import sys

import imp
import os


class PkgLoader(object):
    def install(self):
        sys.meta_path[:] = [x for x in sys.meta_path if self != x] + [self]

    def find_module(self, fullname, path=None):
        return self

    def load_module(self, fullname):
        m_info = fullname
        
        if fullname in sys.modules:
            return sys.modules[fullname]
        parts = fullname.split('.')[1:]
        path = os.path.join(os.path.dirname(__file__), '..')
        # intermediate module
        ns = 'parent.intermediate'
        if ns in sys.modules:
            m = sys.modules[ns]
        elif parts[0] == 'intermediate':
            m = imp.new_module(ns)
            m.__name__ = ns
            m.__path__ = [ns]
            m.__package__ = '.'.join(ns.rsplit('.', 1)[:-1])
        else:
            raise ImportError("Module %s not found." % fullname)
        # submodules
        for p in parts[1:]:
            ns = '%s.%s' % (ns, p)
            fp, filename, options = imp.find_module(p, [path])
            if ns in sys.modules:
                m = sys.modules[ns]
            else:
                m = imp.load_module(ns, fp, filename, options)
                sys.modules[ns] = m
            path = filename
        return m

loader = PkgLoader()
loader.install()