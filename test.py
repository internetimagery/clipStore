import os
import os.path

import collections

class Dict(collections.MutableMapping):
    def __init__(s, *args, **kwargs):
        s.data = dict(*args, **kwargs)
    def __getitem__(s, k): return s.data[k]
    def __setitem__(s, k, v): s.data[k] = v
    def __iter__(s): return iter(s.data)
    def __repr__(s): return repr(s.data)
    def __len__(s): return len(s.data)
    def __delitem__(s): del s.data[k]


d = Dict()
print d
d.update({"one":"two"}, three="four")
print d
