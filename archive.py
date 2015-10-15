# Archive interface
# Created 16/10/15 Jason Dixon
# http://internetimagery.com

import shutil
import os.path
import zipfile
import tempfile
import collections
try:
    import zlib
    compress = zipfile.ZIP_DEFLATED
except ImportError:
    compress = zipfile.ZIP_STORED

class Archive(collections.MutableMapping):
    def __init__(s, path):
        s.mode = "r"
        s.path = path
        s.data = {}
        s.dirty = False
        s.counter = 0
        if os.path.isfile(path):
            with s: s.data = dict((a, str) for a in s.z.namelist())
        else:
            s.mode = "w"
            with s: pass
    def __enter__(s):
        if not s.counter:
            s.z = zipfile.ZipFile(s.path, s.mode, compress)
        s.counter += 1
        return s
    def __exit__(s, *err):
        s.counter -= 1
        s.mode = "r"
        if not s.counter:
            s.z.close()
            if s.dirty:
                s.dirty = False
                tmp = tempfile.mkdtemp()
                try:
                    dirty = set(a for a, b in s.data.items() if b is not str)
                    s.mode = "a"
                    with s:
                        n = set(s.z.namelist())
                        if dirty - n and not dirty & n:
                            for k in dirty:
                                s.z.writestr(k, s.data[k])
                            return
                        s.z.extractall(tmp)
                    paths = dict((a, os.path.realpath(os.path.join(tmp, a))) for a in s.data)
                    s.mode = "w"
                    with s:
                        for k, p in paths.items():
                            if k in dirty:
                                with open(p, "w") as f:
                                    f.write(s.data[k])
                            s.z.write(p, k)
                        s.data = dict((a, str) for a in s.z.namelist())
                finally:
                    shutil.rmtree(tmp)
    def __iter__(s): return iter(s.data)
    def __repr__(s): return repr(s.data)
    def __len__(s): return len(s.data)
    def __getitem__(s, k):
        with s: return s.z.read(k)
    def __setitem__(s, k, v):
        with s:
            s.data[k] = v
            s.dirty = True
    def __delitem__(s, k):
        with s:
            del s.data[k]
            s.dirty = True
