# Clips window

import maya.cmds as cmds

i18n = {
    "clips" : {
        "title"     : "Clips Menu",
        "editChar"  : "Click to change the characters details"
    }
}

class Clips(object):
    def __init__(s, i18n, char, requestCharEdit):
        s.i18n = i18n
        s.char = char
        name = "clipname"

        s.winName = "%sWin" % name
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t=s.i18n["title"])
        cmds.columnLayout(adj=True)
        cmds.rowLayout(nc=2, adj=1)
        cmds.text(
            l="<h1>%s</h1>" % name,
            hl=True,
            h=50
            )
        cmds.iconTextButton(
            ann=i18n["editChar"],
            style="iconOnly",
            font="boldLabelFont",
            image="ghostOff.png",
            h=50,
            w=50,
            bgc=[0.1,0.1,0.1],
            c=requestCharEdit
        )
        cmds.setParent("..") # Close row
        cmds.separator()
        cmds.floatSlider(
            min=50,
            max=200,
            v=100,
            dc=s.sizeClips,
            h=20
            )
        cmds.scrollLayout(cr=True, bgc=[0.2,0.2,0.2], h=400)
        s.wrapper = cmds.gridLayout(cwh=[100, 100], cr=True)
        cmds.showWindow(s.window)
        s.addClips()
    def sizeClips(s, val):
        cmds.gridLayout(s.wrapper, e=True, cwh=[val,val])
    def addClips(s):
        try:
            cmds.deleteUI(cmds.layout(s.wrapper, q=True, ca=True))
        except RuntimeError:
            pass
        for c in range(20):
            cmds.columnLayout(adj=True, bgc=[1,1,1], p=s.wrapper)
            cmds.text(l="HERE")


def test():
    print "edit"

Clips(i18n["clips"], None, test)
