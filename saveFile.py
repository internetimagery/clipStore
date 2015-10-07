# Load and open a savefile for editing. For use with the "with" statement

import tempfile
import zipfile
import os.path
import shutil
import os

class SaveFile(object):
    def __enter__(s, path):
        """
        Open a savefile and return its temporary location
        """
        s.path = path
        s.tempdir = tempfile.mkdtemp()
        if os.path.isfile(path):
            try: # Load our savefile
                store = zipfile.ZipFile(path, "r")
                store.extractall(s.tempdir)
            except (zipfile.BadZipfile, IOError, WindowsError):
                print "File corrupt :: %s." % path
                name, ext = os.path.splitext(path)
                shutil.move(path, "%s(corrupt)%s" % (name, ext))
        else: # Init our save file
            zipfile.ZipFile(path, "w").close()
        return s.tempdir
    def __exit__(s, *errs):
        """
        Update the save file with the changes made
        """
        def storeFile(files=[]):
            for f in files:
                if os.path.isdir(f):
                    for (dirname, dirs, names) in os.walk(f):
                        storeFile(map(lambda x: os.path.join(dirname, x), names))
                else:
                    z.write(f, os.path.relpath(f, s.tempdir))
        try:
            z = zipfile.ZipFile("%s.incomplete" % s.path, "w")
            storeFile([s.tempdir])
            z.close()
            # Replace original
            shutil.move("%s.incomplete" % path, path)
        finally: shutil.rmtree(s.tempdir)
