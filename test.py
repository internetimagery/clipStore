# Testing diff set

import collections

class Diff(collections.MutableSet):
    def __init__(s, *args, **kwargs):
        s._data = set(*args, **kwargs)
        s._diff = set(s._data)
    def __contains__(s, v): return v in s._data
    def __iter__(s): return iter(s._data)
    def discard(s, v): s._data.discard(v)
    def __repr__(s): return repr(s._data)
    def __len__(s): return len(s._data)
    def add(s, v): s._data.add(v)
    def diff():
        doc = "Difference."
        def fget(s):
            add_ = s._data - s._diff
            del_ = s._diff - s._data
            s._diff = set(s._data)
            return [add_, del_]
        return locals()
    diff = property(**diff())


d = Diff()
d.add("one")
print d
print d.diff
print d.diff
