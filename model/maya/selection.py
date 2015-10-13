# Selection functionality

# REDUNDANT? PUTTING THIS INSIDE VIEW!

import maya.cmds as cmds

class Selection(object):
    def current(s):
        """
        Get current selection
        """
        objects = cmds.ls(sl=True)
        channels = cmds.channelBox('mainChannelBox', sma=True, q=True)
        channels = [cmds.attributeQuery(at, n=objects[-1], ln=True) for at in channels] if objects and channels else []
        return dict( (a, [b for b in cmds.listAttr(a, k=True) if not channels or b in channels and cmds.attributeQuery(b, n=a, ex=True)]) for a in cmds.ls(sl=True, type="transform") )

Selection = Selection()
