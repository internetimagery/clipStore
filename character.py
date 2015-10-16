# Character. Loaded from clips file
# Created 10/10/15 Jason Dixon
# http://internetimagery.com

import collections
import reference
import tempfile
import inspect
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
#               data.json
#               thumbs/
#                   1.png
#                   2.png
#                   ...


class Path(str):
    """
    Temporary path
    """
    def __del__(s):
        if os.path.isfile(s):
            print "Cleaning up", s
            os.remove(s)
    def __getattribute__(s, k):
        raise AttributeError, "\"Path\" cannot be modified with \"%s\"" % k

class Dirty(collections.MutableMapping):
    def __init__(s, dictionary):
        s.data = dictionary
        s._dirty = False
    def __getitem__(s, k): return s.data[k]
    def __iter__(s): return iter(s.data)
    def __repr__(s): return repr(s.data)
    def __len__(s): return len(s.data)
    def __setitem__(s, k, v):
        s.data[k] = v
        s._dirty = True
    def __delitem__(s, k):
        del s.data[k]
        s._dirty = True
    def dirty():
        doc = "Track Changes"
        def fget(s):
            v = s._dirty
            s._dirty = False
            return v
        def fset(s, v):
            s._dirty = v
        return locals()
    dirty = property(**dirty())

class Encoder(json.JSONEncoder):
    _types = [dict, list]
    def default(s, o):
        for t in s._types:
            try:
                return t(o)
            except: pass
        return json.JSONEncoder.default(s, o)
def encode(*args, **kwargs): return json.dumps(*args, indent=4, cls=Encoder, **kwargs)
def decode(*args, **kwargs): return json.loads(*args, **kwargs)

class Clip(object):
    """
    Single Clip
    """
    def __init__(s, ID):
        s.ID = ID # Location of the clip in savefile
        s.data = {} # { Obj , { Attribute, [ value, value, ... ] } }
        s.thumbs = [] # Store thumbnails
        s.metadata = Dirty({
            "createdOn" : time.time(),
            "createdBy" : getpass.getuser()
            })

class Character(object):
    """
    Character. Contains data for clips.
    """
    def __init__(s, path, software):
        new = False if os.path.isfile(path) else True
        s.archive = archive.Archive(path)
        s.metadata = {
            "createdOn" : time.time(),
            "createdBy" : getpass.getuser(),
            "name"      : os.path.basename(os.path.splitext(path)[0]),
            "software"  : software
            }

        with s.archive:
            s.metadata = Dirty(dict(s.metadata, **decode(s.archive.get("metadata.json", "{}")))) # Metadata
            s.ref = Dirty(reference.Reference(decode(s.archive.get("reference.json", "{}")))) # Reference file
            s.data = Dirty(dict(decode(s.archive.get("data.json", "{}")))) # Storage
            if new:
                s.metadata.dirty = True
                s.data.dirty = True
                s.ref.dirty = True
            tree = dict((a, a.split("/")) for a in s.archive.keys())
            clipIDs = set(b[1] for a, b in tree.items() if b[0] == "clips" )
            s.clips = set() # Clips
            if clipIDs:
                for ID in clipIDs:
                    c = Clip(ID)
                    c.metadata = Dirty(dict(c.metadata, **decode(s.archive.get("clips/%s/metadata.json" % ID, "{}"))))
                    c.data = decode(s.archive.get("clips/%s/data.json", "{}"))
                    thumbs = sorted([a for a, b in tree.items() if b[0] == "clips" and b[1] == ID and b[2] == "thumbs"])
                    if thumbs:
                        for th in thumbs:
                            c.thumbs.append(s.cache(th))
                    s.clips.add(c)

    def save(s):
        """
        Save data
        """
        with s.archive:
            if s.metadata.dirty: s.archive["metadata.json"] = encode(s.metadata)
            if s.ref.dirty: s.archive["reference.json"] = encode(s.ref)
            if s.data.dirty: s.archive["data.json"] = encode(s.data)
            # CLIPS STUFF
            tree = dict((a, a.split("/")) for a in s.archive.keys())
            diff1 = set(b[1] for b in tree.values() if b[0] == "clips")
            diff2 = set(a.ID for a in s.clips)
            new_ = diff2 - diff1 # New clips
            del_ = diff1 - diff2 # Removed clips
            if s.clips:
                for c in s.clips:
                    ID = c.ID
                    if c.metadata.dirty or ID in new_: s.archive["clips/%s/metadata.json" % ID] = encode(c.metadata)
                    if ID in new_: # New clip
                        s.archive["clips/%s/data.json" % ID] = encode(c.data)
                        if c.thumbs:
                            for i, th in enumerate(c.thumbs):
                                with open(th, "rb") as f:
                                    s.archive["clips/%s/thumbs/%s%s" % (ID, i, os.path.splitext(str(th))[1])] = f.read()
            if del_:
                for k, v in tree.items():
                    try:
                        if v[1] in del_:
                            del s.archive[k]
                    except IndexError: pass

    def createClip(s):
        """
        Generate a new clip.
        """
        c = Clip(uuid.uuid4().hex) # Create a new clip ID
        s.clips.add(c)
        return c

    def removeClip(s, clip):
        """
        Remove clip
        """
        s.clips.remove(clip)

    def cache(s, path):
        """
        Pull out a file that can be interracted with.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(path)[1]) as tmp:
            tmp.write(s.archive[path])
        return Path(tmp.name)
