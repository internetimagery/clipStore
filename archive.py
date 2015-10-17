# Archive interface
# Created 16/10/15 Jason Dixon
# http://internetimagery.com

import shutil
import os.path
import zipfile
import collections
try:
    import zlib
    compress = zipfile.ZIP_DEFLATED
except ImportError:
    compress = zipfile.ZIP_STORED

class Archive(collections.MutableMapping):
    def __init__(s, path):
        s._depth = 0
        s._mode = "r"
        s._path = path
        s._dirty = False
        if os.path.isfile(path):
            with s: s._data = dict((a, file) for a in s.z.namelist())
        else:
            s._data = {}
            s._mode = "w"
            with s: pass
    def __enter__(s):
        if not s._depth:
            s.z = zipfile.ZipFile(s._path, s._mode, compress)
        s._depth += 1
        return s
    def __exit__(s, *err):
        s._depth -= 1
        s._mode = "r"
        if not s._depth:
            if s._dirty:
                s._dirty = False
                dirty = set(a for a, b in s._data.items() if b is not file)
                n = set(s.z.namelist())
                if dirty - n and not dirty & n:
                    s.z.close()
                    s._mode = "a"
                    with s:
                        for k in dirty:
                            s.z.writestr(k, s._data[k])
                else:
                    read = s.z
                    s._mode = "w"
                    path, s._path = s._path, "%s.incomplete" % s._path
                    try:
                        with s:
                            s.z.comment = read.comment
                            for k in s._data:
                                if k in dirty:
                                    s.z.writestr(k, s._data[k])
                                else:
                                    s.z.writestr(k, read.read(k))
                        read.close()
                        shutil.move(s._path, path)
                    finally:
                        s._path = path
                s._data = dict((a, file) for a in s.z.namelist())
            else:
                s.z.close()
    def __iter__(s): return iter(s._data)
    def __repr__(s): return repr(s._data)
    def __len__(s): return len(s._data)
    def __getitem__(s, k):
        with s: return s.z.read(k)
    def __setitem__(s, k, v):
        with s:
            s._data[k] = v
            s._dirty = True
    def __delitem__(s, k):
        with s:
            del s._data[k]
            s._dirty = True
