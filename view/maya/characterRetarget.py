# Edit the character

import maya.cmds as cmds
# import warn
import animCopy.view.maya.warn as warn

i18n = {
    "characterRetarget" : {
        "title" : "Retarget Objects / Attributes",
        "return": "Return to Character Edit window",
        "from"  : "FROM",
        "to"    : "TO"
    }
}

class CharacterRetarget(object):
    def __init__(s, i18n, char, requestEdit, requestObjects, sendRetarget):
        s.i18n = i18n
        s.char = char
        s.requestObjects = requestObjects
        s.sendRetarget = sendRetarget
        name = s.char.metadata["name"].title()

        s.objClose = {} # Close state of obj
        s.filterBox = {} # Storing filter bloxes for dynamic updates

        winName = "CharacterEditWin"
        if cmds.window(winName, ex=True): cmds.deleteUI(winName)
        s.window = cmds.window(t="%s :: %s" % (s.i18n["title"], name), rtf=True)
        cmds.columnLayout(adj=True)
        # Title
        cmds.text(l="<h1>%s</h1>" % name)
        # Top button
        cmds.iconTextButton(
            l=s.i18n["return"],
            image="goToBindPose.png",
            style="iconAndTextHorizontal",
            c=lambda: warn.run(requestEdit, s.char)
        )
        cmds.separator()
        s.colWidth = 300
        s.rowHeight = 30
        cmds.rowLayout(nc=2)
        cmds.text(l=i18n["from"], w=s.colWidth)
        cmds.text(l=i18n["to"], w=s.colWidth)
        cmds.setParent("..")
        cmds.scrollLayout(h=400, w=s.colWidth*2, bgc=[0.2,0.2,0.2])
        s.wrapper = cmds.columnLayout(adj=True)
        cmds.showWindow(s.window)
        cmds.scriptJob(uid=[s.window, s.save], ro=True)
        s.refresh()

    def clear(s, element):
        ch = cmds.layout(element, q=True, ca=True)
        if ch:
            for c in ch:
                try: cmds.deleteUI(c)
                except RuntimeError: pass

    def refresh(s, *dump): # Build out GUI
        # Clear GUI
        s.clear(s.wrapper)
        # Get data to build
        data = s.requestObjects(s.char)
        # Build out panels in sync
        if data:
            for obj, attrs in data.items():
                if attrs:
                    # Put in some objects
                    put1, put2 = s.addObj(obj)
                    for attr, val in attrs.items():
                        s.addAttr(attr, put1, put2)

    def addObj(s, obj):
        """
        Add object.
        """
        objDown = "v %s" % obj
        objUp = "^ %s" % obj
        def sync():
            val = cmds.layout(row1, q=True, m=True)
            val = False if val else True
            cmds.button(objBtn, e=True, l=objUp if val else objDown)
            cmds.layout(row1, e=True, m=val)
            cmds.layout(row2, e=True, m=val)

        row = cmds.rowLayout(nc=2, cw2=[s.colWidth, s.colWidth], p=s.wrapper)
        # FROM COLUMN!
        cmds.columnLayout(adj=True, w=s.colWidth, p=row)
        objBtn = cmds.button(
            l=objDown,
            h=s.rowHeight,
            bgc=[0.3,0.3,0.3],
            c=lambda x: sync()
        )
        row1 = cmds.columnLayout(adj=True, m=False)
        # TO COLUMN
        cmds.columnLayout(adj=True, w=s.colWidth, p=row)
        cmds.button(
            l=obj,
            h=s.rowHeight,
            )
        row2 = cmds.columnLayout(adj=True, m=False)
        return row1, row2

    def addAttr(s, attr, parent1, parent2):
        # Insert FROM
        cmds.text(
            l=attr,
            h=s.rowHeight,
            p=parent1
            )
        cmds.button(
            l=attr,
            h=s.rowHeight,
            p=parent2
            )

    def save(s):
        s.char.save()
