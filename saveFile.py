# Load and open a savefile for editing. For use with the "with" statement
# Created 10/10/15 Jason Dixon
# http://internetimagery.com

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

class SaveFile(object):
    def __init__(s, path):
        s.path = path # Where does this savefile live?
        if os.path.isdir(s.path): raise IOError, "Path provided is not a file."
    def pull(s, paths):
        """
        Pull out group of files into temporary locations.
        Return function responsible for cleaning it up.
        """
        def cleanup():
            try:
                shutil.rmtree(tmp)
            except IOError:
                pass
        if os.path.isfile(s.path):
            files = {}
            tmp = tempfile.mkdtemp() # Temp file
            try:
                z = zipfile.ZipFile(s.path, "r")
                names = z.namelist()
                for path in paths:
                    if path in names:
                        z.extract(path, tmp)
                        files[path] = os.path.realpath(os.path.join(tmp, path))
            except (zipfile.BadZipfile, IOError, WindowsError):
                cleanup()
            s.cacheFiles.append(cleanup)
            return files, cleanup
    def __enter__(s):
        """
        Open a savefile and return its temporary location using "with"
        """
        s.tempdir = tempfile.mkdtemp()
        if os.path.isfile(s.path):
            try: # Load our savefile
                with Timer("Reading file"):
                    store = zipfile.ZipFile(s.path, "r")
                    store.extractall(s.tempdir)
            except (zipfile.BadZipfile, IOError, WindowsError):
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
            with Timer("Saving file"):
                z = zipfile.ZipFile("%s.incomplete" % s.path, "w")
                for f in s.listFiles([s.tempdir]):
                    z.write(f, os.path.relpath(f, s.tempdir))
                z.close()
                # Replace original
                shutil.move("%s.incomplete" % s.path, s.path)
        finally: shutil.rmtree(s.tempdir)
