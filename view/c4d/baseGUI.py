# Base for gui windows

import c4d
import c4d.gui as gui
from collections import defaultdict as dd

class Window(gui.geDialog):
    """
    Generic window
    """
    def __init__(s):
        s._widgets = {} # Widgets we want to keep track of
        s._events = dd(set) # Tracking events
        s._idStart = 4000 # Where do we want to start our ID's?
        gui.geDialog.__init__(s)
    def CreateLayout(s):
        raise NotImplementedError, "Forgot to override \"CreateLayout\"."
        return True
    def Command(s, id, msg):
        if id in s._widgets and callable(s._widgets[id]):
            s._widgets(id, msg)
        return True
    def CoreMessage(s, id, msg):
        if id in s._events and s._events[id]:
            for call in s._events[id]:
                if callable(call): call(id, msg)
        return True
    def Bind(s, id, func):
        if id in s._widgets:
            raise RuntimeError, "ID: %s is already bound!" % id
        else:
            s._widgets[id] = func
    def Unbind(s, id=None, func=None):
        if id:
            if id in s._widgets:
                del s._widgets[id]
        elif func:
            for a, b in s._widgets.items():
                if func == b:
                    del s._widgets[a]
        else:
            raise RuntimeError, "No ID or Function provided."
    def ID(s):
        id = s._idStart
        while id in s._widgets: id += 1
        s.Bind(id, None)
        return id
    def BindEvent(s, id, func): s._events[id].add(func)
    def UnbindEvent(s, func):
        if s._events:
            for id in s._events:
                if func in s._events[id]: s._events[id].remove(func)
