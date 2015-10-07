# Not really needed...
import tempfile
import zipfile
import os.path
import shutil
import os
import re

class FileSystem(object):
    def __init__(s, path):
        """
        Working with a savefile
        """
        s.path = path
        s.tempdir = tempfile.mkdtemp()
        if os.path.isfile(path):
            try: # Load our savefile
                store = zipfile.ZipFile(path, "r")
                try:
                    store.extractall(s.tempdir)
                except (IOError, WindowsError):
                    raise IOError, "Failed to load the file %s" % path
            except zipfile.BadZipfile:
                print "File corrupt."
                name, ext = os.path.splitext(path)
                shutil.move(path, "%s(corrupt)%s" % (name, ext))
        else: # Init our save file
            zipfile.ZipFile(path, "w").close()
    def _formpath(s, path):
        if path:
            if os.path.isabs(path):
                path = re.sub(r"^(\/|[A-Za-z]:[\\\/])", "", path)
            return os.path.realpath(os.path.join(s.tempdir, path))
        raise IOError, "No file provided."
    def open(s, path, mode="r", buffering=-1):
        path = s._formpath(path)
        if "w" in mode:
            try: os.makedirs(os.path.dirname(path))
            except: pass
        return open(path, mode, buffering)
    def remove(s, path):
        path = s._formpath(root)
        if os.path.isdir(path): os.removedirs(path)
        elif os.path.isfile(path):
            os.remove(path)
            try: os.removedirs(os.path.dirname(path))
            except OSError: pass
    def listdir(path): return os.listdir(s._formpath(path))
    def save(s): # USE THIS TO PERSIST CHANGES!
        def storeFile(files=[]):
            for f in files:
                if os.path.isdir(f):
                    for (dirname, dirs, names) in os.walk(f):
                        storeFile(map(lambda x: os.path.join(dirname, x), names))
                else:
                    z.write(f, os.path.relpath(f, s.tempdir))
        z = zipfile.ZipFile("%s.incomplete" % s.path, "w")
        storeFile([s.tempdir])
        z.close()
        # Replace original
        shutil.move("%s.incomplete" % path, path)
    def __del__(s):
        shutil.rmtree(s.tempdir)
