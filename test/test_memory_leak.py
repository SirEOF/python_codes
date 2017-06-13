import gc


class SelfLoop():
    def __init__(self):
        self.loop = self
        pass


class SelfLoopDel():
    def __init__(self):
        self.loop = self
        pass

    def __del__(self):
        """
        if you add this will fuck up
        :return: 
        """
        del self


def make_leak():
    a = SelfLoop()
    b = SelfLoopDel()
    a, b = None, None
    gc.collect()
    print gc.garbage


if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_OBJECTS)
    # del SelfLoopDel.__del__
    make_leak()
