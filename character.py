# Character. Loaded from clips file

import os.path
import getpass
import time
import uuid
import json
import os

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
            "name"          : "CLIP", # Name of the clip
            "length"        : 0, # Length of the clip
            "createdOn"     : time.time(),
            "createdBy"     : getpass.getuser(),
            "modifiedOn"    : time.time(),
            "modifiedBy"    : getpass.getuser()
        }
        s.clipData = {} # { ID , { Attribute, [ value, value ... ] } }
        if root: # We want to load this information. Otherwise creating new
            # Load Metadata
            metaFile = os.path.join(root, "metadata.json")
            s.metadata = UpdateData(metaFile, s.metadata, lambda x, y: dict(x, **y))
            # Load Clip Data
            clipFile = os.path.join(root, "metadata.json")
            s.clipData = UpdateData(clipFile, s.clipData, lambda x, y: dict(x, **y))
        s.thumbs = {} # {small : Path, medium : Path, large : Path}
        s.tempThumb = {} # {small : Path, medium : Path, large : Path}

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
        s.reference = [] # [ [ UUID : Object ] ]
        s.clips = [] # List of clips
        # Load our Data
        with s.saveFile as sf:
            # Load Metadata
            metaFile = os.path.join(sf, "metadata.json")
            s.metadata = UpdateData(metaFile, s.metadata, lambda x, y: dict(x, **y))
            # Load ID References
            refFile = os.path.join(sf, "reference.json")
            s.reference = UpdateData(refFile, s.reference, lambda x, y: y)
            # Load clips
            clipsFile = os.path.join(sf, "clips")
            if os.path.isdir(clipsFile):
                clips = os.listdir()
                if clips: # We have some existing clips to load
                    for ID in clips:
                        try:
                            s.clips.append(Clip(s, ID, os.path.join(clips, ID)))
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
                json.dump(s.reference, f)
            # Save Clips
            clipsFile = os.path.join(sf, "clips")
            if not os.path.isdir(clipsFile): os.mkdir(clipsFile)
            for clip in s.clips:
                print "add in clip save functionality, espeically thumbs"
    def getReference(s, item):
        """
        Add / Retrieve an item / reference
        Using references means we can change the info in one place,
        without breaking all the clips.
        """
        if item:
            if not s.reference: s.reference = [[],[]]
            try: return s.reference[s.reference[0].index(item)][0]
            except ValueError: pass
            try: return s.reference[s.reference[1].index(item)][0]
            except ValueError: pass
            s.reference[0].append(str(uuid.uuid4())) # UUID
            s.reference[1].append(item)

root = os.path.dirname(__file__)
import sys
sys.path.append(root)
path = os.path.join(root, "savefile.zip")

import saveFile

c = Character(path, "maya")
print c.getReference("pSphere1")
c.save()
