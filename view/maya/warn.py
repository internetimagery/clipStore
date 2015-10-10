# Visual warning popup on error

import maya.cmds as cmds

class Warn(object):
    def __enter__(s):
        return None
    def __exit__(s, type, err, trace):
        if err:
            cmds.confirmDialog(t="Uh oh...", m=str(err))
Warn = Warn()
