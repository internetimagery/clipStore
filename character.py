# Character. Loaded from clips file
# Created 10/10/15 Jason Dixon
# http://internetimagery.com

import reference
import tempfile
import os.path
import getpass
import archive
import shutil
import time
import uuid
import json
import os

# Structure:
#
# metadata.json
# reference.json
# data.json
# clips/
#       clipname/
#               metadata.json
#               clip.json
#               small.thumb
#               medium.thumb
#               large.thumb


class Temp_Path(str):
    def __del__(s):
        if os.path.isfile(s):
            print "Cleaning up", s
            os.remove(s)
    def __getattribute__(s, k):
        raise AttributeError, "\"Temp_Path\" cannot be modified with \"%s\"" % k


class Clip(object):
    """
    Single Clip
    """
    def __init__(s, ID, root=None):
        s.ID = ID # Location of the clip in savefile
        s.metadata = {
            "createdOn"     : time.time(),
            "createdBy"     : getpass.getuser(),
            "modifiedOn"    : time.time(),
            "modifiedBy"    : getpass.getuser(),
            "thumbs"        : {} # Thumbnails!
        }
        s.clip = {} # { Obj , { Attribute, [ value, value ... ] } }
        if root: # We want to load this information. Otherwise creating new
            root = os.path.join(root, ID)
            # Load Metadata
            metaFile = os.path.join(root, "metadata.json")
            s.metadata = UpdateData(metaFile, s.metadata, lambda x, y: dict(x, **y))
            # Load Clip Data
            clipFile = os.path.join(root, "clip.json")
            s.clip = UpdateData(clipFile, s.clip, lambda x, y: dict(x, **y))
        s.cleanup = [] # Temp files that might need to be cleaned?

    def _save(s, root):
        """
        Executed by the Character. Save the data to its own space
        """
        root = os.path.join(root, s.ID)
        if not os.path.isdir(root): os.mkdir(root)
        # Save images
        for name, path in s.metadata["thumbs"].items():
            if os.path.isabs(path) and os.path.isfile(path): # Path has been changed to something new!
                filename = str(name) + os.path.splitext(str(path))[1] # Make a filename
                localPath = os.path.join(root, filename)
                shutil.copyfile(path, localPath) # Copy image over
                s.metadata["thumbs"][name] = "clips/%s/%s" % (s.ID, filename)
        # Save metadata
        s.metadata["modifiedOn"] = time.time()
        s.metadata["modifiedBy"] = getpass.getuser()
        with open(os.path.join(root, "metadata.json"), "w") as f:
            json.dump(s.metadata, f, indent=4)
        # Save clip data
        with open(os.path.join(root, "clip.json"), "w") as f:
            json.dump(s.clip, f, indent=4)


class Character(object):
    """
    Character. Contains data for clips.
    """
    def __init__(s, path, software):
        s.archive = archive.Archive(path)
        s.metadata = {
            "name"        : os.path.basename(os.path.splitext(path)[0]),
            "createdOn"   : time.time(),
            "createdBy"   : getpass.getuser(),
            "modifiedOn"  : time.time(),
            "modifiedBy"  : getpass.getuser(),
            "software"    : software
            }
        with s.archive:
            s.metadata = dict(s.metadata, **s.archive.get("metadata.json", {})) # Metadata
            s.ref = reference.Reference(s.archive.get("reference.json", {})) # Reference file
            s.data = s.archive.get("data.json", {}) # Storage
            s.clips = [] # Clips


            # # Load clips
            # clipsFile = os.path.join(sf, "clips")
            # if os.path.isdir(clipsFile):
            #     clips = os.listdir(clipsFile)
            #     if clips: # We have some existing clips to load
            #         for ID in clips:
            #             try:
            #                 s.clips.append(Clip(ID, clipsFile))
            #             except IOError:
            #                 print "Failed to load clip %s." % clip

    def save(s):
        """
        Save data
        """
        with s.archive:
            s.archive["metadata.json"] = json.dumps(s.metadata, indent=4)
            s.archive["reference.json"] = json.dumps(s.ref, indent=4, cls=reference.ReferenceEncode)
            s.archive["data.json"] = json.dumps(s.data, indent=4)
            # CLIPS STUFF

            #
            # # Save Clips
            # clipsFile = os.path.join(sf, "clips")
            # if not os.path.isdir(clipsFile): os.mkdir(clipsFile)
            # for clip in s.clips:
            #     clip._save(clipsFile)

    def createClip(s):
        """
        Create a new clip.
        """
        c = Clip(uuid.uuid4().hex) # Create a new clip ID
        s.clips.append(c)
        return c

    def removeClip(s, clip):
        """
        Remove clip
        """
        if clip in s.clips:
            ID = clip.ID
            with s.archive:
                for k in s.archive.keys():
                    if ID in k: del s.archive[k]
        else:
            raise RuntimeError, "Clip not found..."

    def cache(s, path):
        """
        Wrapper for savefile extract
        Pull out requested file into temporary file to work with.
        """
        ext = os.path.splitext(path)[1]
        data = s.archive[path]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(data)
        return Temp_Path(tmp.name)


root = os.path.realpath(os.path.join(os.path.dirname(__file__), "test.zip"))
c = Character(root, "maya")
