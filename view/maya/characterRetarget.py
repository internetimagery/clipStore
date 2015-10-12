# Edit the character

import maya.cmds as cmds
# import warn
import animCopy.view.maya.warn as warn

i18n = {
    "characterRetarget" : {
        "title" : "Retarget Objects / Attributes",
        "return": "Return to Character Edit window"
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
            c=lambda: warn.run(requestEdit)
        )
        cmds.separator()
        rows = cmds.rowLayout(nc=2, adj=2)
        cmds.columnLayout(adj=True, p=rows)
        cmds.text(l="FROM")
        s._from = cmds.scrollLayout(h=400, cr=True, bgc=[0.2,0.2,0.2])
        cmds.columnLayout(adj=True, p=rows)
        cmds.text(l="TO")
        s.to = cmds.scrollLayout(h=400, cr=True, bgc=[0.2,0.2,0.2])
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
        s.clear(s._from)
        s.clear(s.to)
        s.fromFrame = {}
        s.toFrame = {}
        # Get data to build
        data = s.requestObjects(s.char)
        # Build out panels in sync
        if data:
            for obj, attrs in data.items():
                if attrs:
                    # Put in some objects
                    put1 = s.addObj1(obj)
                    put2 = s.addObj2(obj)
                    for attr, val in attrs.items():
                        s.addAttr1(attr, obj, put1)
                        s.addAttr2(attr, obj, put2)

    def addObj1(s, obj):
        """
        Add object to "from" field.
        """
        def sync(val):
            cmds.frameLayout(
                s.toFrame[obj],
                e=True,
                cl=val
            )
        return cmds.frameLayout(
            l=obj,
            cll=True,
            cl=True,
            cc=lambda: warn.run(sync, True),
            ec=lambda: warn.run(sync, False),
            bgc=[0.3,0.3,0.3],
            p=s._from
            )

    def addObj2(s, obj):
        """
        Add object to "from" field.
        """
        def sync(val):
            cmds.frameLayout(
                s.fromFrame[obj],
                e=True,
                cl=val
            )
        return cmds.frameLayout(
            l=obj,
            cll=True,
            cl=True,
            cc=lambda: warn.run(sync, True),
            ec=lambda: warn.run(sync, False),
            bgc=[0.3,0.3,0.3],
            p=s._from
            )

    def addAttr1(s, attr, obj, parent):
        cmds.text(l=attr, p=parent)

    def addAttr2(s, attr, obj, parent):
        cmds.text(l=attr, p=parent)

    def save(s):
        s.char.save()
