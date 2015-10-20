# Base for gui windows

import c4d
import c4d.gui as gui

class Window(gui.geDialog):
    """
    Generic window
    """
    def __init__(s):
        s._widgets = {}
        s._idStart = 4000 # Where do we want to start our ID's?
        gui.geDialog.__init__(s)
    def CreateLayout(s):
        raise NotImplementedError, "Override \"CreateLayout\"."
    def Command(s, id, msg):
        if id in s._widgets and callable(s._widgets[id]):
            s._widgets(id, msg)
    def Bind(s, id, func):
        if id in s._widgets:
            raise RuntimeError, "ID: %s is already bound!" % id
        else:
            s._widgets[id] = func
    def Unbind(s, id=None, func=None):
        if id:
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
