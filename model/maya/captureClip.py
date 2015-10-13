# Capture a pose or animation given a character

import maya.cmds as cmds

def CaptureAnim(character, frames):
    """
    Capture a characters current pose or animation information
    """
    structure = {}
    # Validate information
    if frames and len(frames) == 2:
        frames = sorted(frames)
        for frame in range(frames[0], frames[1] + 1):
            cmds.currentTime(frame) # Move to frame
            for obj in character:
                if structure.has_key(obj) or cmds.objExists(obj):
                    structure[obj] = structure.get(obj, {})
                    for at in character[obj]:
                        if structure[obj].has_key(at) or cmds.attributeQuery(at, n=obj, ex=True):
                            structure[obj][at] = structure[obj].get(at, [])
                            structure[obj][at].append(cmds.getAttr("%s.%s" % (obj, at)))
    else:
        raise RuntimeError, "Frame range not valid."
    return structure
