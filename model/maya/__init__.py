# Gathering all the GUI elements into one place!

import sys as _sys
class Package(object):
    def __init__(s, local):
        import os.path
        s.cache = {}
        s.local = dict((k, local[k]) for k in local)
        s.root = os.path.realpath(os.path.dirname(s.local["__file__"]))
    def __getattr__(s, k):
        if k in s.local: return s.local[k]
        if k in s.cache: return s.cache[k]
        path = list(s.local["_sys"].path)
        s.local["_sys"].path = [s.root]
        try:
            module = __import__(k)
            name = k[0].capitalize() + k[1:]
            s.cache[k] = getattr(module, name) if hasattr(module, name) else module
        finally: s.local["_sys"].path[:] = path
        return s.cache[k]
_sys.modules[__name__] = Package(locals())
