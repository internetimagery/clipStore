# Capture a pose or animation given a character
# Created 13/10/15 Jason Dixon
# http://internetimagery.com

import maya.cmds as cmds
from collections import defaultdict as dd

def CaptureClip(data, frames):
    """
    Capture a characters current pose or animation information
    Accepts =
        data = { object : [ attribute ] }
        frames = [frameStart, frameEnd]
    """
    newData = dd(lambda:dd(list))
    frames = sorted(frames)
    oldFrame = cmds.currentTime(q=True) # Mark where we were
    for frame in range(int(frames[0]), int(frames[1] + 1)):
        cmds.currentTime(frame) # Move to frame
        for obj, attrs in data.items():
            if attrs and obj in newData or cmds.objExists(obj):
                for attr in attrs:
                    if attr in newData[obj] or cmds.attributeQuery(attr, n=obj, ex=True):
                        newData[obj][attr].append(cmds.getAttr("%s.%s" % (obj, attr)))
    cmds.currentTime(oldFrame) # Put us back where we started
    return newData
