# coding=utf-8
""" This Version is deprecated. Please use the newest version
This version adapt the import hook to implement the profile. It's really a bad design.

The newest version will use the `sys.setprofile` to implement the function with a better and clean design. 
"""

# deprecated
__version__ = '0.1.0'

from profiler import install_importer, activate_timing, show_timing_cost

__all__ = [
    'install_importer',
    'activate_timing',
    'show_timing_cost',
]
