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
    def __init__(s):
        s.clipData = {} # {ID.Attribute : [value, value, value]}
        s.thumbs = {} # {small : Path, medium : Path, large : Path}
        s.tempThumb = {} # {small : Path, medium : Path, large : Path}

# Structure:
#
# metadata.json
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
        s.clips = [] # List of clips
        # Load our Data
        with s.saveFile as s:
            metafile = os.path.join(s, "metadata.json")
            if os.path.isfile(metafile): # Metadata exists, update ours
                with open(metafile) as f:
                    try:
                        data = json.load(f)
                        s.metadata = dict(s.metadata, **data)
                    except (ValueError, IndexError):
                        print "Unable to load metadata"
            clipsFile = os.path.join(s, "clips")
            if os.path.isdir(clipsFile):
                clips = os.listdir()
                if clips: # We have some existing clips to load
                    for clip in clips:
                        clipsData = os.path.join(clipsFile, clip, "data.json")


        s.idReference = {} # Reference ID's with Obj identifiers

root = os.path.dirname(__file__)
import sys
sys.path.append(root)
path = os.path.join(root, "savefile.clips")

import saveFile

Character(path, "maya")
