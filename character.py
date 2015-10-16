# Character. Loaded from clips file
# Created 10/10/15 Jason Dixon
# http://internetimagery.com
try:
    import cPickle as pickle
except ImportError:
    import pickle
import collections
import reference
import StringIO
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
            print "Cleaning up %s" % s
            os.remove(s)
    def __getattribute__(s, k):
        if k[0] == "_": return str.__getattribute__(s, k)
        raise AttributeError, "\"Path\" cannot be modified with \"%s\"" % k

class Dict(collections.MutableMapping):
    """
    Wrapper to track changes. Changes = [New, Changed, Removed]
    """
    def __init__(s, dictionary):
        s._data = dictionary
        s._diff = {}; s.diff
    def __getitem__(s, k): return s._data[k]
    def __setitem__(s, k, v): s._data[k] = v
    def __iter__(s): return iter(s._data)
    def __repr__(s): return repr(s._data)
    def __delitem__(s, k): del s._data[k]
    def __len__(s): return len(s._data)
    def _hash(s, o):
        f = StringIO.StringIO()
        p = pickle.Pickler(f, -1)
        p.persistent_id = s._filter
        p.dump(o); f.seek(0)
        return f.read()
    def _filter(s, o):
        try:
            return pickle.dumps(o)
        except:
            return str(o.__class__)
    def diff():
        def fget(s):
            diff1 = set([a for a in s._data]) # Current keys
            diff2 = set([a for a in s._diff]) # Old keys
            diff3 = dict((a, s._hash(b)) for a, b in s._data.items()) # Changes
            new = diff1 - diff2 # New keys
            rem = diff2 - diff1 # Removed keys
            chg = set(a for a, b in diff3.items() if a in s._diff and a not in new and a not in rem and b != s._diff[a])
            s._diff = diff3
            return [new, chg, rem] if new or chg or rem else None
        def fset(s, v):
            if v:
                s._diff = {}
            else:
                s.diff
        return locals()
    diff = property(**diff())

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
        s.metadata = Dict({
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
            s.metadata = Dict(dict(s.metadata, **decode(s.archive.get("metadata.json", "{}")))) # Metadata
            s.ref = Dict(reference.Reference(decode(s.archive.get("reference.json", "{}")))) # Reference file
            s.data = Dict(decode(s.archive.get("data.json", "{}"))) # Storage
            if new:
                s.metadata.diff = True
                s.data.diff = True
                s.ref.diff = True
            tree = dict((a, a.split("/")) for a in s.archive.keys())
            clipIDs = set(b[1] for a, b in tree.items() if b[0] == "clips" )
            s.clips = Dict({})
            if clipIDs:
                for ID in clipIDs:
                    c = Clip(ID)
                    c.metadata = Dict(dict(c.metadata, **decode(s.archive.get("clips/%s/metadata.json" % ID, "{}"))))
                    c.data = decode(s.archive.get("clips/%s/data.json" % ID, "{}"))
                    thumbs = sorted([a for a, b in tree.items() if b[0] == "clips" and b[1] == ID and b[2] == "thumbs"])
                    if thumbs:
                        for th in thumbs:
                            c.thumbs.append(s.cache(th))
                    s.clips[ID] = c
            s.clips.diff

    def save(s):
        """
        Save data
        """
        with s.archive:
            if s.metadata.diff: s.archive["metadata.json"] = encode(s.metadata)
            if s.ref.diff: s.archive["reference.json"] = encode(s.ref)
            if s.data.diff: s.archive["data.json"] = encode(s.data)
            # CLIPS STUFF
            tree = dict((a, a.split("/")) for a in s.archive.keys())
            diff1 = set(b[1] for b in tree.values() if b[0] == "clips")
            diff2 = set(a for a in s.clips)
            new_ = diff2 - diff1 # New clips
            del_ = diff1 - diff2 # Removed clips
            changes = s.clips.diff
            if changes:
                for ID, c in s.clips.items():
                    if c.metadata.diff or ID in changes[0]: s.archive["clips/%s/metadata.json" % ID] = encode(c.metadata)
                    if ID in changes[0]: # New clip
                        s.archive["clips/%s/data.json" % ID] = encode(c.data)
                        if c.thumbs:
                            for i, th in enumerate(c.thumbs):
                                with open(th, "rb") as f:
                                    s.archive["clips/%s/thumbs/%s%s" % (ID, i, os.path.splitext(str(th))[1])] = f.read()
                if changes[2]:
                    for k, v in tree.items():
                        try:
                            if v[1] in changes[2]:
                                del s.archive[k]
                        except IndexError: pass

    def createClip(s):
        """
        Generate a new clip.
        """
        c = Clip(uuid.uuid4().hex) # Create a new clip ID
        s.clips[c.ID] = c
        return c

    def removeClip(s, clip):
        """
        Remove clip
        """
        del s.clips[clip.ID]

    def cache(s, path):
        """
        Pull out a file that can be interracted with.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(path)[1]) as tmp:
            tmp.write(s.archive[path])
        return Path(tmp.name)
