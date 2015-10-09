# Reverse lookup dict

import collections
import uuid
import json

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
