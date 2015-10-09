# Retarget items to other items.

import maya.cmds as cmds

i18n = {
    "retarget"  : {
        "title" : "Retarget",
        "desc"  : "Select an object and click the button to retarget."
    }
}

class Retarget(object):
    def __init__(s, i18n, targets, requestTarget):
        s.i18n = i18n
        s.targets = targets # Targets to retarget
        s.requestTarget = requestTarget # ask for a retarget

        s.winName = "RetargetWin"
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t=s.i18n["title"])
        cmds.columnLayout(adj=True)
        cmds.text(l=i18n["desc"])
        cmds.separator()
        cmds.rowLayout(nc=3, adj=2)
        s.old = cmds.columnLayout(adj=True) # Start Row
        cmds.setParent("..") # End Row
        s.sep = cmds.columnLayout(adj=True) # Start Row
        cmds.setParent("..") # End Row
        s.new = cmds.columnLayout(adj=True) # Start Row
        cmds.setParent("..") # End Row
        s.buildItems()
        cmds.showWindow(s.window)
    def clear(s, elem):
        ch = cmds.layout(elem, ca=True)
        if ch:
            for c in ch:
                try:
                    cmds.deleteUI(c)
                except RuntimeError:
                    pass
    def buildItems(s):
        if s.targets:
            def addTarget(item):
                def sendtarget():
                    try:
                        name = s.requestTarget(item)
                        if name:
                            cmds.button(btn, e=True, l=name)
                    except RuntimeError as e:
                        cmds.confirmDialog(t="uh oh...", m=str(e))
                height = 30
                cmds.text(l=item, p=s.old, h=height)
                cmds.iconTextStaticLabel(
                    style="iconOnly",
                    image="hsDownStreamCon.png",
                    p=s.sep,
                    h=height
                    )
                btn = cmds.button(
                    l=item,
                    p=s.new,
                    h=height,
                    c=lambda x: sendtarget()
                    )
                pass
            for target in s.targets:
                addTarget(target)

def testObj(obj):
    sel = cmds.ls(sl=True, type="transform")
    if len(sel):
        return sel[0]
    raise RuntimeError, "Only one object should be selected."

Retarget(i18n["retarget"], range(10), testObj)
