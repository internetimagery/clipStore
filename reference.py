# Reverse lookup dict that tracks values with IDs

import collections
import uuid
import json

class Dict(collections.MutableMapping):
    """
    Double Indexed Dict
    """
    def __init__(s, *args, **kwargs):
        s.fwd = dict(*args, **kwargs)
        s.rev = dict((v, k) for k, v in s.fwd.items())
    def __delitem__(s, k):
        if k in s.fwd: return s.rev.pop(s.fwd.pop(k))
        if k in s.rev: return s.fwd.pop(s.rev.pop(k))
        raise KeyError, "%s not found." % k
    def __getitem__(s, k):
        if k in s.fwd: return s.fwd[k]
        if k in s.rev: return s.rev[k]
        raise KeyError, "%s not found." % k
    def __iter__(s): return iter(s.fwd)
    def __repr__(s): return repr(s.fwd)
    def __len__(s): return len(s.fwd)
    def __setitem__(s, k, v):
        try: s.__delitem__(k)
        except KeyError: pass
        try: s.__delitem__(v)
        except KeyError: pass
        s.fwd[k] = v
        s.rev[v] = k

class Reference(Dict):
    def __getitem__(s, k):
        """
        Attempts to get missing key can add key with ID
        """
        try:
            return Dict.__getitem__(s, k)
        except KeyError:
            id = uuid.uuid4().hex
            Dict.__setitem__(s, id, k)
            return id
    def __setitem__(s, k, v):
        """
        Only allow matching ID's to keys
        """
        try:
            uuid.UUID(k)
            Dict.__setitem__(s, k, v)
        except ValueError:
            raise KeyError, "%s is not an ID." % k

class ReferenceEncode(json.JSONEncoder):
    """
    Allow encoding References
    """
    def default(s, obj):
        if isinstance(obj, Reference): return obj.fwd
        return json.JSONEncoder.default(s, obj)
