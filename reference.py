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
    def __len__(s): return len(s.fwd)
    def __repr__(s): return repr(s.fwd)
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

class Reference(collections.MutableMapping):
    """
    Store items as references so they can be changed later without,
    breaking anything.
    """
    def __init__(s, *args, **kwargs):
        temp = dict(*args, **kwargs)
        s._ref = {}
        for k, v in temp.items(): # Validate keys and init dict:
            try: s._ref[uuid.UUID(k).hex] = v
            except ValueError: # Maybe keys are in wrong order?
                try: s._ref[uuid.UUID(v).hex] = k
                except ValueError: # Invalid
                    print "%s invalid ID. Skipping." % k
        s._item = dict((v, k) for k, v in s._ref.items())
    def __getitem__(s, k):
        print "GETTING", k
        try: return s._ref[k] # return item if id is given
        except KeyError:
            try: return s._item[k] # return id if item is given
            except KeyError: # Item not yet in here. Add it!
                id = uuid.uuid4().hex
                s._ref[id] = k
                s._item[k] = id
                return id
    def __setitem__(s, k, v): # Change reference
        del s._item[s._ref[k]]
        s._ref[k] = v
        s._item[v] = k
    def __delitem__(s, k): # Delete reference
        del s._item[s._ref[k]]
        del s._ref[k]
    def __iter__(s): return iter(s._ref)
    def __len__(s): return len(s._ref)
    def __repr__(s): return repr(s._ref)

class ReferenceEncode(json.JSONEncoder):
    """
    Allow encoding References
    """
    def default(s, obj):
        if isinstance(obj, Reference): return obj._ref
        return json.JSONEncoder.default(s, obj)


# class Reference(dict):
#     def __init__(s, *args, **kwargs):
#         temp1 = dict(*args, **kwargs)
#         temp2 = {}
#         for k, v in temp1.items(): # Validate keys and init dict:
#             try: temp2[str(uuid.UUID(k).hex)] = v
#             except ValueError: # Maybe keys are in wrong order?
#                 try: temp2[str(uuid.UUID(v).hex)] = k
#                 except ValueError: # Invalid
#                     print "%s invalid ID. Skipping." % k
#         s._item = dict((v, k) for k, v in temp2.items())
#         dict.__init__(s, temp2)
#     def __getitem__(s, k):
#         try: return dict.__getitem__(s, k) # return item if id is given
#         except KeyError:
#             try: return s._item[k] # return id if item is given
#             except KeyError: # Item not yet in here. Add it!
#                 id = str(uuid.uuid4().hex)
#                 dict.__setitem__(s, id, k)
#                 s._item[k] = id
#                 return id
#     def __setitem__(s, k, v): # Change reference
#         del s._item[dict.__getitem__(s, k)]
#         dict.__setitem__(s, k, v)
#         s._item[v] = k
#     def __delitem__(s, k): # Delete reference
#         del s._item[dict.__getitem__(s, k)]
#         dict.__delitem__(s, k)
#     def get(s, k, default=None): return s.__getitem__(k)




r = Reference()
r["gone"] = "here"
r["another"] = 3
del r["gone"]
print r[3]
