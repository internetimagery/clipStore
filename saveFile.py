# Load and open a savefile for editing. For use with the "with" statement
# Created 10/10/15 Jason Dixon
# http://internetimagery.com

import threading
import tempfile
import zipfile
import os.path
# import hashlib # Faster to simply save the file back than check for changes
import shutil
import time
import os

profile = True
class Timer(object):
    def __init__(s, name):
        s.name = name
    def __enter__(s):
        s.start = time.time()
        return s
    def __exit__(s, *args):
        if profile:
            s.end = time.time()
            s.secs = s.end - s.start
            s.msecs = s.secs * 1000  # millisecs
            print '%s...\t\tElapsed time: %f ms' % (s.name, s.msecs)

class Temp_Path(str):
    def __del__(s):
        if os.path.isfile(s):
            print "Cleaning up", s
            os.remove(s)
    def __getattribute__(s, k):
        raise AttributeError, "\"Temp_Path\" cannot be modified with \"%s\"" % k

class SaveFile(object):
    def __init__(s, path):
        s.path = path # Where does this savefile live?
        if os.path.isdir(s.path): raise IOError, "Path provided is not a file."

    def extract(s, filename):
        """
        Pull out file into temporary location.
        Returns path to file.
        """
        try:
            z = zipfile.ZipFile(s.path, "r")
            names = z.namelist()
            if filename in names:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as f:
                    f.write(z.read(filename))
                return Temp_Path(f.name)
        except (zipfile.BadZipfile, IOError, OSError):
            raise IOError, "%s not in Save file." % filename

    def __enter__(s):
        """
        Open a savefile and return its temporary location using "with"
        """
        s.tempdir = tempfile.mkdtemp()
        if os.path.isfile(s.path):
            try: # Load our savefile
                with Timer("Opening file"):
                    store = zipfile.ZipFile(s.path, "r")
                    store.extractall(s.tempdir)
            except (zipfile.BadZipfile, IOError, OSError):
                print "File corrupt :: %s." % s.path
                name, ext = os.path.splitext(s.path)
                shutil.move(s.path, "%s(corrupt)%s" % (name, ext))
        else: # Init our save file
            zipfile.ZipFile(s.path, "w").close()
        return s.tempdir
    def listFiles(s, files, func=None):
        info = {}
        for f in files:
            if os.path.isdir(f):
                for (dirname, dirs, names) in os.walk(f):
                    info = dict(info, **s.listFiles(map(lambda x: os.path.join(dirname, x), names), func))
            else:
                info[f] = func(f) if func else None
        return info
    # def checksum(s, path):
    #     h = hashlib.md5()
    #     with open(path, "rb") as f:
    #         while True:
    #             data = f.read(8192)
    #             if not data:
    #                 break
    #             h.update(data)
    #     return h.hexdigest()
    def __exit__(s, *errs):
        """
        Update the save file with the changes made
        """
        try:
            with Timer("Closing file"):
                z = zipfile.ZipFile("%s.incomplete" % s.path, "w")
                for f in s.listFiles([s.tempdir]):
                    z.write(f, os.path.relpath(f, s.tempdir))
                z.close()
                # Replace original
                shutil.move("%s.incomplete" % s.path, s.path)
        finally: shutil.rmtree(s.tempdir)
