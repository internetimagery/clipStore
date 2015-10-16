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
#               clip.json
#               thumbs/
#                   1.png
#                   2.png
#                   ...


class Path(str):
    """
    Self cleaning path
    """
    def __del__(s):
        if os.path.isfile(s):
            print "Cleaning up", s
            os.remove(s)
    def __getattribute__(s, k):
        raise AttributeError, "\"Path\" cannot be modified with \"%s\"" % k

def Dirty(func):
    def wrapper(s, *args, **kwargs):
        s.dirty = True
        return func(s, *args, **kwargs)
    return wrapper

class Dict(collections.MutableMapping):
    def __init__(s, *args, **kwargs):
        s.data = dict(*args, **kwargs); s.dirty = False
    def __getitem__(s, k): return s.data[k]
    def __iter__(s): return iter(s.data)
    def __repr__(s): return repr(s.data)
    def __len__(s): return len(s.data)
    @Dirty
    def __setitem__(s, k, v): s.data[k] = v
    @Dirty
    def __delitem__(s): del s.data[k]

class Ref(reference.Reference):
    def __init__(s, *args, **kwargs):
        reference.Reference.__init__(s, *args, **kwargs); s.dirty = False
    @Dirty
    def __setitem__(s, k, v): return reference.Reference.__setitem__(s, k, v)
    @Dirty
    def __delitem__(s, k): return reference.Reference.__delitem__(s, k)

class Encoder(json.JSONEncoder):
    s._types = [dict, list]
    def default(self, o):
        for t in s._types:
            try:
                return t(o)
            except: pass
        return json.JSONEncoder.default(s, o)
def encode(*args, **kwargs): return json.dumps(*args, cls=Encoder, **kwargs)
def decode(*args, **kwargs): return json.loads(*args, **kwargs)

def Metadata(data=None):
    if not data:
        data = {
            "createdOn"     : time.time(),
            "createdBy"     : getpass.getuser()
            }
    return dict(data, **{
        "modifiedOn"    : time.time(),
        "modifiedBy"    : getpass.getuser()
    }

class Clip(object):
    """
    Single Clip
    """
    def __init__(s, ID, new=False):
        s.new = new
        s.ID = ID # Location of the clip in savefile
        s.metadata = Dict(Metadata())
        s.data = {} # { Obj , { Attribute, [ value, value, ... ] } }
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
    def __init__(s, path, software, new=False):
        s.archive = archive.Archive(path)
        s.metadata = Metadata()
        s.metadata["name"] = os.path.basename(os.path.splitext(path)[0]),
        s.metadata["software"] = software

        with s.archive:
            s.metadata = Dict(s.metadata, **decode(s.archive.get("metadata.json", {}))) # Metadata
            s.ref = Ref(decode(s.archive.get("reference.json", {}))) # Reference file
            s.data = Dict(decode(s.archive.get("data.json", {}))) # Storage
            tree = dict((a, a.split("/")) for a in s.archive.keys())
            clipIDs = set(b[1] for a, b in tree.items() if b[0] == "clips" )
            s.clips = set() # Clips
            if clipIDs:
                for ID in clipIDs:
                    c = Clip(ID)
                    c.thumbs = sorted([a, for a, b in tree.items() if b[0] == "clips" and b[1] == c and b[2] == "thumbs"])
                    c.metadata = Dict(c.metadata, **decode(s.archive.get("clips/%s/metadata.json" % ID, {})))
                    c.clip = decode(s.archive.get("clips/%s/clip.json" % ID, {}))

    def save(s):
        """
        Save data
        """
        with s.archive:
            if s.metadata.dirty or s.new: s.archive["metadata.json"] = encode(s.metadata)
            if s.ref.dirty or s.new: s.archive["reference.json"] = encode(s.ref)
            if s.data.dirty or s.new: s.archive["data.json"] = encode(s.data)
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
                    if ID in new_:
                        s.archive["clips/%s/clip.json" % ID] = c.clip
                        if c.thumbs:
                            for i, th in enumerate(c.thumbs):
                                with open(th, "rb") as f:
                                    s.archive["clips/%s/thumbs/%s.png" % (ID, i)] = f.read()
            if del_:
                for k, v in tree.items():
                    if v[1] in del_:
                        del s.archive[k]



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
        Pull out a file that can be interracted with.
        """
        ext = os.path.splitext(path)[1]
        data = s.archive[path]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(data)
        return Path(tmp.name)


root = os.path.realpath(os.path.join(os.path.dirname(__file__), "test.zip"))
c = Character(root, "maya")
