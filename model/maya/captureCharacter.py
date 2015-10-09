# Capture a characters information with optional filters
import maya.cmds as cmds

def CaptureCharacter(objects=None, whitelist=None, blacklist=None):
    """
    Grab objects and attributes that form a character
    """
    objects = cmds.ls(objects, type="transform") if objects else cmds.ls(sl=True, type="transform")
    if not objects:
        raise RuntimeError, "No usable objects."
    whitelist = set(whitelist) if whitelist else None
    blacklist = set(blacklist) if blacklist else None
    structure = {}
    for obj in objects:
        attrs = set(cmds.listAttr(obj, k=True))
        if whitelist:
            attrs = attrs & whitelist
        if blacklist:
            attrs = attrs - blacklist
        if attrs:
            structure[obj] = list(attrs)
    return structure
