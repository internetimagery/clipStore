# Testing zipfile functionality

import zipfile
import os.path

path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "ziptest.zip")
path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "view.zip")

import collections

# class Store(collections.MutableMapping):
#     """
#     Save files all together
#     """
#     def load(s, path):
#         s.path = path # Path to data file
#         if os.path.isfile(path):
#             s.store = zipfile.ZipFile(path, "r")
#         else:
#             s.store = None
#         s.cache = dict((p, None) for p in s.store.namelist())
#     def __getitem__(s, k):
#         k = k.replace("\\", "/")
#         if k not in s.cache:
#             if not s.cache[k]:
#                 if k[-1:] == "/": # Directory
#                     s.cache[k] = [p.replace(k, "") for p in s.cache if k in p and p != k]
#                 elif s.store: # File
#                     s.cache[k] = s.store.open(k)
#             return s.cache[k]
#         else:
#             raise KeyError, "%s not in storage" % k
#         return s.cache[k]
#     def __init__(s, path): s.load(path)
#     def __setitem__(s, k, v): s.cache[k.replace("\\", "/")] = v
#     def __delitem__(s, k): del s.cache[k]
#     def __iter__(s): return iter(s.cache)
#     def __len__(s): return len(s.cache)
#     def __del__(s): s.store.close()

import tempfile
import os.path
import os
import re
import shutil

class Store(object):
    def __init__(s, path):
        """
        Working with a savefile
        """
        s.list = []
        s.path = path
        if os.path.isfile(path):
            try: # Load our savefile
                store = zipfile.ZipFile(path, "r")
                s.list = [p for p in s.store.namelist()]
            except zipfile.BadZipfile:
                print "File corrupt."
        else: # Init our save file
            zipfile.ZipFile(path, "w").close()
        s.tempdir = tempfile.mkdtemp()
    def _formpath(s, path):
        if path:
            if os.path.isabs(path):
                path = re.sub(r"^(\/|[A-Za-z]:[\\\/])", "", path)
            return os.path.realpath(os.path.join(s.tempdir, path))
        raise IOError, "No file provided."
    def open(s, path, mode="r", buffering=-1):
        path = s._formpath(path)
        if "w" in mode: os.makedirs(os.path.dirname(path))
        return open(path, mode, buffering)
    def mkdir(s, path, *args, **kwargs):
        return os.makedirs(s._formpath(path), *args, **kwargs)
    def __del__(s):
        print "cleaning up tempfiles"
        shutil.rmtree(s.tempdir)

path = os.path.join(
    os.path.realpath(
        os.path.dirname(__file__)
        ),
    "myfile.char")

d = Store(path)
with d.open("hone/two/three.txt", "w") as f:
    print f.name
# if os.path.isfile(path):
#     z = zipfile.ZipFile(path, "r")
#     print z.namelist()
#     z.close()
# else:
#     raise IOError, "zip not found"
