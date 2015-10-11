# Selection functionality

import maya.cmds as cmds

class Selection(object):
    def allAttributes(s, objects=None):
        """
        Provide all attributes from given selected objects
        """
        objects = cmds.ls(objects, type="transform") if objects else cmds.ls(sl=True, type="transform")
        if objects:
            return list(set(cmds.listAttr(objects, keyable=True)))
        else:
            raise RuntimeError, "No usable objects."
    def getSelection(s, objects=None):
        """
        Get selection, objects and attributes
        """
        sel = cmds.ls(sl=True, type="transform")
        if sel:
            store = {}
            for s in sel:
                store[s] = cmds.listAttr(s, k=True)
            return store
        else: raise RuntimeError, "Nothing selected."
