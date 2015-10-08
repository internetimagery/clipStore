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
        s.clipData = {} # { Obj , { Attribute, [ value, value ... ] } }
        if root: # We want to load this information. Otherwise creating new
            root = os.path.join(root, ID)
            # Load Metadata
            metaFile = os.path.join(root, "metadata.json")
            s.metadata = UpdateData(metaFile, s.metadata, lambda x, y: dict(x, **y))
            # Load Clip Data
            clipFile = os.path.join(root, "clip.json")
            s.clipData = UpdateData(clipFile, s.clipData, lambda x, y: dict(x, **y))
        s.thumbs = {} # {small : Path, medium : Path, large : Path}
        s.tempThumb = {} # {small : Path, medium : Path, large : Path}
    def save(s, root):
        """
        Run by the Character. Save the data to its own space
        """
        root = os.path.join(root, s.ID)
        if not os.path.isdir(root): os.mkdir(root)
        # Save metadata
        s.metadata["modifiedOn"] = time.time()
        s.metadata["modifiedBy"] = getpass.getuser()
        with open(os.path.join(root, "metadata.json"), "w") as f:
            json.dump(s.metadata, f)
        # Save clip data
        with open(os.path.join(root, "clip.json"), "w") as f:
            json.dump(s.clipData, f)

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
                json.dump(s.reference, f)
            # Save Clips
            clipsFile = os.path.join(sf, "clips")
            if not os.path.isdir(clipsFile): os.mkdir(clipsFile)
            for clip in s.clips:
                clip.save(clipsFile)
    def getReference(s, item):
        """
        Add / Retrieve an item / reference
        Using references means we can change the info in one place,
        without breaking all the clips.
        Excessive referencing might bulk it up a bit though...
        """
        if item:
            if not s.reference: s.reference = [[],[]]
            try: return s.reference[1][s.reference[0].index(item)]
            except ValueError: pass
            try: return s.reference[0][s.reference[1].index(item)]
            except ValueError: pass
            s.reference[0].append(str(uuid.uuid4())) # UUID
            s.reference[1].append(item) # Add the item
            return s.reference[0][-1]
    def replaceReference(s, ID, item):
        """
        What would referencing be without the ability to replace.
        Given the ID and item, replace!
        """
        if ID and item:
            try:
                i = s.reference[0].index(ID)
                s.reference[1][i] = item
            except ValueError:
                raise RuntimeError, "ID not found in reference."
    def removeReference(s, ID):
        """
        Get rid of a reference
        """
        if ID:
            try:
                i = s.reference[0].index(ID)
                del s.reference[0][i] # Removed ID
                del s.reference[1][i] # Remove item
            except ValueError:
                raise RuntimeError, "ID not found in reference."
    def createClip(s):
        """
        Create a new clip.
        """
        c = Clip(s, str(uuid.uuid4())) # Create a new clip
        s.clips.append(c)
        return c

root = os.path.dirname(__file__)
import sys
sys.path.append(root)
path = os.path.join(root, "savefile.zip")

import saveFile

c = Character(path, "maya")
ref = c.getReference("pSphere1")
print ref
c.replaceReference(ref, "pSphere3")
print c.getReference(ref)
print c.createClip()
c.save()
