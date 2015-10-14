# Selection functionality
# Created 14/10/15 Jason Dixon
# http://internetimagery.com

import maya.cmds as cmds

class Selection(object):
    def current(s):
        """
        Get current selection
        Return { object : { attribute : True/False } }
        """
        objects = cmds.ls(sl=True, type="transform")
        channels = cmds.channelBox('mainChannelBox', sma=True, q=True)
        channels = [cmds.attributeQuery(at, n=objects[-1], ln=True) for at in channels] if objects and channels else []
        return dict( (a.replace(cmds.ls(a, sns=True)[1], "").replace(":", ""), dict((b, True if not channels or b in channels else False) for b in cmds.listAttr(a, k=True) if cmds.attributeQuery(b, n=a, ex=True))) for a in objects )

Selection = Selection()
