# Output a list of all unique attributes in selection

import maya.cmds as cmds

def AllAttriutes(objects=None):
    """
    Provide all attributes from all selected objects
    """
    objects = cmds.ls(objects, type="transform") if objects else cmds.ls(sl=True, type="transform")
    if objects:
        return list(set(cmds.listAttr(objects, keyable=True)))
    else:
        raise RuntimeError, "No usable objects."
