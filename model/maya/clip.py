# Capture or pose an animation given a character
# Created 13/10/15 Jason Dixon
# http://internetimagery.com

import maya.cmds as cmds
from collections import defaultdict as dd

class Clip(object):
    def capture(s, data, frames):
        """
        Capture a characters current pose or animation information
        Accepts =
            data = { object : { attribute : None } }
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
    def replay(s, data):
        """
        Places the data back onto the objects in the scene at the current time.
        Accepts = { object : { attribute : [val1, val2, val3, ... ] } }
        """
        frame = cmds.currentTime(q=True) # Current time to start at
        index = 0 # Current index
        # Validate objects and build a working set of data
        validData = {}
        for o, attrs in data.items():
            if cmds.objExists(o): # Check for object existance
                for at in attrs:
                    if cmds.attributeQuery(at, n=o, ex=True):
                        validData["%s.%s" % (o, at)] = data[o][at]
                    else:
                        print "%s.%s could not be found. Skipping!" % (o, at)
            else:
                print "%s could not be found. Skipping!" % o
        # Ok our data is now valid. Lets get a posin! Phew. The final step...
        try:
            # Flip the values for more efficient function calls
            while True:
                cache = dd(list)
                for o, val in validData.items():
                    cache[val[index]].append(o)
                for val, o in cache.items(): # Keyframe the positions
                    cmds.setKeyframe(o, t=frame, v=val)
                frame += 1
                index += 1
        except IndexError:
            pass

Clip = Clip()
