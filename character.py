# Character. Loaded from clips file
# Created 10/10/15 Jason Dixon
# http://internetimagery.com

import reference
import saveFile
import os.path
import getpass
import image
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

def UpdateData(filename, dataOld, func):
    """
    Update data given existing file
    """
    try:
        with open(filename) as f:
            try:
                dataNew = json.load(f)
                dataOld = func(dataOld, dataNew)
            except (ValueError, IndexError):
                print "Failed to update data %s." % filename
    except IOError: pass
    return dataOld

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
                filename = name + os.path.splitext(str(path))[1] # Make a filename
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
    Character. Contains many clips
    """
    def __init__(s, path, software):
        s.saveFile = saveFile.SaveFile(path) # Path to savefile
        s.metadata = {
            "name"        : os.path.basename(os.path.splitext(path)[0]),
            "createdOn"   : time.time(),
            "createdBy"   : getpass.getuser(),
            "modifiedOn"  : time.time(),
            "modifiedBy"  : getpass.getuser(),
            "software"    : software
            }
        s.ref = reference.Reference() # Reference object
        s.data = {} # Storage
        s.clips = [] # List of clips
        # Load our Data
        with s.saveFile as sf:
            # Load Metadata
            metaFile = os.path.join(sf, "metadata.json")
            s.metadata = UpdateData(metaFile, s.metadata, lambda x, y: dict(x, **y))
            # Load ID References
            refFile = os.path.join(sf, "reference.json")
            s.ref = UpdateData(refFile, s.ref, lambda x, y: reference.Reference(y))
            # Load Data
            dataFile = os.path.join(sf, "data.json")
            s.data = UpdateData(dataFile, s.data, lambda x, y: dict(x, **y))
            # Load clips
            clipsFile = os.path.join(sf, "clips")
            if os.path.isdir(clipsFile):
                clips = os.listdir(clipsFile)
                if clips: # We have some existing clips to load
                    for ID in clips:
                        try:
                            s.clips.append(Clip(ID, clipsFile))
                        except IOError:
                            print "Failed to load clip %s." % clip
    def save(s):
        """
        Store data in save file
        """
        with s.saveFile as sf:
            # Save Metadata
            s.metadata["modifiedOn"] = time.time()
            s.metadata["modifiedBy"] = getpass.getuser()
            metaFile = os.path.join(sf, "metadata.json")
            with open(metaFile, "w") as f:
                json.dump(s.metadata, f, indent=4)
            # Save Reference
            refFile = os.path.join(sf, "reference.json")
            with open(refFile, "w") as f:
                json.dump(s.ref, f, cls=reference.ReferenceEncode, indent=4)
            # Save Data
            dataFile = os.path.join(sf, "data.json")
            with open(dataFile, "w") as f:
                json.dump(s.data, f, indent=4)
            # Save Clips
            clipsFile = os.path.join(sf, "clips")
            if not os.path.isdir(clipsFile): os.mkdir(clipsFile)
            for clip in s.clips:
                clip._save(clipsFile)
    def createClip(s):
        """
        Create a new clip.
        """
        c = Clip(uuid.uuid4().hex) # Create a new clip
        s.clips.append(c)
        return c
    def cache(s, files):
        """
        Wrapper for savefile extract
        Pull out requested files into temporary files.
        """
        return s.saveFile.extract(files)
