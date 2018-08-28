from __future__ import print_function

import sys


class SerialDebug():
    debug = False



    @classmethod
    def debug_var(cls, expression):
        if cls.debug:
            frame = sys._getframe(1)
            print(expression, '=', repr(eval(expression, frame.f_globals, frame.f_locals)))

    def set_debug(self, flag=True):
        setattr(self.__class__, "debug", flag)

    @classmethod
    def debug_print(cls, msg):
        if cls.debug:
            print("debug: " + msg)
