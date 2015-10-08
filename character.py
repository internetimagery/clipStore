# Character. Loaded from clips file

import os.path
import getpass
import time
import json
import os

class Clip(object):
    """
    Single Clip
    """
    def __init__(s, path=None):
        s.path = path # Location of the clip
        s.clipData = {} # {ID.Attribute : [value, value, value]}
        s.thumbs = {} # {small : Path, medium : Path, large : Path}
        s.tempThumb = {} # {small : Path, medium : Path, large : Path}

# Structure:
#
# metadata.json
# reference.json
# clips/
#       clipname/
#               data.json
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
        s.reference = {} # ID references
        s.clips = [] # List of clips
        # Load our Data
        with s.saveFile as sf:
            # Load Metadata
            metaFile = os.path.join(sf, "metadata.json")
            if os.path.isfile(metaFile): # Metadata exists, update ours
                with open(metaFile) as f:
                    try:
                        data = json.load(f)
                        s.metadata = dict(s.metadata, **data)
                    except (ValueError, IndexError):
                        print "Unable to load metadata"
            # Load ID References
            refFile = os.path.join(sf, "reference.json")
            if os.path.isfile(refFile):
                with open(refFile) as f:
                    try:
                        data = json.load(f)
                        s.reference = dict(s.reference, **data)
                    except (ValueError, IndexError):
                        print "Unable to load reference Data"
            # Load clips
            clipsFile = os.path.join(sf, "clips")
            if os.path.isdir(clipsFile):
                clips = os.listdir()
                if clips: # We have some existing clips to load
                    for clip in clips:
                        clipsData = os.path.join(clipsFile, clip, "data.json")
                        if os.path.isfile(clipsData): # Is the file here?
                            try:
                                s.clips.append(Clip(clipsData))
                            except IOError:
                                print "Failed to load clip %s." % clip
    def save(s):
        """
        Store data in save file
        """
        with s.saveFile as sf:
            # Save Metadata
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



root = os.path.dirname(__file__)
import sys
sys.path.append(root)
path = os.path.join(root, "savefile.clips")

import saveFile

Character(path, "maya").save()
