try:
    import cPickle as pickle
except ImportError:
    import pickle
import collections
import StringIO

class Dict(collections.MutableMapping):
    """
    Wrapper to track changes. Changes = [New, Changed, Removed]
    """
    def __init__(s, dictionary=None):
        s._data = dictionary if dictionary else {}
        s._diff = {}; s.diff
    def __getitem__(s, k): return s._data[k]
    def __setitem__(s, k, v): s._data[k] = v
    def __iter__(s): return iter(s._data)
    def __repr__(s): return repr(s._data)
    def __len__(s): return len(s._data)
    def __delitem__(s, k): del s._data[k]
    def _hash(s, o):
        f = StringIO.StringIO()
        p = pickle.Pickler(f, -1)
        p.persistent_id = s._filter
        p.dump(o); f.seek(0)
        return f.read()
    def _filter(s, o):
        try:
            return pickle.dumps(o)
        except:
            return str(o.__class__)
    def diff():
        def fget(s):
            diff1 = set([a for a in s._data]) # Current keys
            diff2 = set([a for a in s._diff]) # Old keys
            diff3 = dict((a, s._hash(b)) for a, b in s._data.items()) # Changes
            new = diff1 - diff2 # New keys
            rem = diff2 - diff1 # Removed keys
            chg = set(a for a, b in diff3.items() if a in s._diff and a not in new and a not in rem and b != s._diff[a])
            s._diff = diff3
            return [new, chg, rem] if new or chg or rem else None
        def fset(s, v):
            if v:
                s._diff = {}
            else:
                s.diff
        return locals()
    diff = property(**diff())

d = Dict()
d["one"] = "two"
print d.diff
d["one"] = "three"
d["two"] = "things"
del d["one"]
print d.diff
# del d["one"]
print d.diff
