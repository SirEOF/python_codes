# coding=utf8

import pprint

old_printer = pprint.PrettyPrinter


class PrettyPrinter(old_printer):
    def format(self, obj, context, maxlevels, level):
        if isinstance(obj, unicode):
            return obj.encode('utf8'), True, False
        return old_printer.format(self, obj, context, maxlevels, level)


def monkey_patch_pprint():
    pprint.PrettyPrinter = PrettyPrinter
