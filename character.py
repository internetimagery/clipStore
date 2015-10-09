# Character. Loaded from clips file

### REMOVE THIS
import os.path
import sys
root = os.path.dirname(__file__)
sys.path.append(root)
#####

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
    def __init__(s, character, ID, root=None):
        s.character = character # Character that houses this clip
        s.ID = ID # Location of the clip in savefile
        s.metadata = {
            "createdOn"     : time.time(),
            "createdBy"     : getpass.getuser(),
            "modifiedOn"    : time.time(),
            "modifiedBy"    : getpass.getuser(),
            "thumbSmall"    : image.small, # Thumbnail for clip
            "thumbLarge"    : image.large # Also a thumnail
        }
        s.clipData = {} # { Obj , { Attribute, [ value, value ... ] } }
        if root: # We want to load this information. Otherwise creating new
            root = os.path.join(root, ID)
            # Load Metadata
            metaFile = os.path.join(root, "metadata.json")
            s.metadata = UpdateData(metaFile, s.metadata, lambda x, y: dict(x, **y))
            # Load Clip Data
            clipFile = os.path.join(root, "clip.json")
            s.clipData = UpdateData(clipFile, s.clipData, lambda x, y: dict(x, **y))
    def save(s, root):
        """
        Run by the Character. Save the data to its own space
        """
        root = os.path.join(root, s.ID)
        if not os.path.isdir(root): os.mkdir(root)
        # Save images
        for key, name in {
            "thumbLarge" : "large",
            "thumbSmall" : "small"
            }.iteritems():
            path = s.metadata[key]
            if os.path.isabs(path):
                fn = name + os.path.splitext(path)[1]
                if os.path.isfile(path):
                    shutil.copyfile(path, os.path.join(root, fn))
                s.metadata[key] = fn
        # Save metadata
        s.metadata["modifiedOn"] = time.time()
        s.metadata["modifiedBy"] = getpass.getuser()
        with open(os.path.join(root, "metadata.json"), "w") as f:
            json.dump(s.metadata, f)
        # Save clip data
        with open(os.path.join(root, "clip.json"), "w") as f:
            json.dump(s.clipData, f)

class Character(object):
    """
    Character. Contains many clips
    """
    def __init__(s, path, software):
        s.saveFile = saveFile.SaveFile(path) # Path to savefile
        s.metadata = {
            "createdOn"   : time.time(),
            "createdBy"   : getpass.getuser(),
            "modifiedOn"  : time.time(),
            "modifiedBy"  : getpass.getuser(),
            "software"    : software
            }
        s.ref = reference.Reference() # Reference object
        s.clips = [] # List of clips
        # Load our Data
        with s.saveFile as sf:
            # Load Metadata
            metaFile = os.path.join(sf, "metadata.json")
            s.metadata = UpdateData(metaFile, s.metadata, lambda x, y: dict(x, **y))
            # Load ID References
            refFile = os.path.join(sf, "reference.json")
            s.ref = UpdateData(refFile, s.ref, lambda x, y: reference.Reference(y))
            # Load clips
            clipsFile = os.path.join(sf, "clips")
            if os.path.isdir(clipsFile):
                clips = os.listdir(clipsFile)
                if clips: # We have some existing clips to load
                    for ID in clips:
                        try:
                            s.clips.append(Clip(s, ID, clipsFile))
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
                json.dump(s.metadata, f)
            # Save Reference
            refFile = os.path.join(sf, "reference.json")
            with open(refFile, "w") as f:
                json.dump(s.ref, f, cls=reference.ReferenceEncode)
            # Save Clips
            clipsFile = os.path.join(sf, "clips")
            if not os.path.isdir(clipsFile): os.mkdir(clipsFile)
            for clip in s.clips:
                clip.save(clipsFile)
    def createClip(s):
        """
        Create a new clip.
        """
        c = Clip(s, uuid.uuid4().hex) # Create a new clip
        s.clips.append(c)
        return c
