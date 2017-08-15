# coding=utf-8
"""
This is a module about `MEMORY`, Python has its `this`, And we have `that`

Winner Winner Chicken Dinner.

@author: weidwonder
"""
import random

import sys

nest = [
    u"抸磧辽,,杍嫑鈝	泧9还釋幵丌昮乇乇哑+笫䷿丩抸丹三壯+笫事丩丹干壯+辽丹兤壯",
    u"	@9亿乇昮眞止皃轥祝>	P9轥祝尰昮旟讹剌斸皃遒跮月夙乇皃良隽咋陨阺+郼覀䷿彿旟剌 	归焵+成皃耀优讠+丌箠还亚陨阺昮丌"
    u"昮抣跮皃轭胍		→轥祝	,,,,'?[	,,,,,^^^^^^^^^\^Z^^.^=^^^^^^^^^^"
    u"^^^^^^^^^^^^	,,.^^^^[;={^^^^[{<<<<<<<<<<<<<<{	,,<[^.^^[^[^^^^^^^{^.^^[^^C<<"
    u"<<<<<<<<<<<<	^^^^^^^^'^^(^^^^^^^^^^^^^'^^(^^^^^^^^{<<<<<<<<<<<<<<{^^	",
    u"帥钰亅吖>沠月+丌甧拄忂+叮令讨佟堁元皃衧姏皃哤哤仗钰"
]


def give_me_an_egg(your_call):
    return u''.join(map(lambda c: unichr(ord(c) - 1), your_call))


def break_my_egg(egg):
    return u''.join(map(lambda c: unichr(ord(c) + 1), egg))


def wait_for_dinner():
    def except_hook(exctype, value, traceback):
        print break_my_egg(random.choice(nest))
        sys.__excepthook__(exctype, value, traceback)

    sys.excepthook = except_hook
