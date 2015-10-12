# Edit the character

import maya.cmds as cmds
# import warn
import animCopy.view.maya.warn as warn

i18n = {
    "characterRetarget" : {
        "title"         : "Retarget Objects / Attributes",
        "return"        : "Return to Character Edit window",
        "from"          : "FROM",
        "to"            : "TO",
        "fromDesc"      : "Click for more information.",
        "toDesc"        : "Select the desired object / attribute and click the button.",
        "confirm"       : "Just confirming...",
        "targetConfirm" : "Try and be sure the new target shares similar object names and attribute names.\nThings can break if you're not careful.\nAre you sure?",
        "yes"           : "Yes",
        "no"            : "No"
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
        cmds.rowLayout(nc=3, adj=2)
        cmds.text(l=i18n["from"], w=s.colWidth)
        cmds.text(l="  >  ", h=s.rowHeight)
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
        # List everything:
        s.allItems = set()
        # Build out panels in sync
        if data:
            for obj in sorted(data.keys()):
                attrs = data[obj]
                if attrs:
                    # Put in some objects
                    s.allItems.add(obj)
                    put1, put2, put3 = s.addObj(obj)
                    for attr in sorted(attrs.keys()):
                        s.allItems.add(attr)
                        s.addAttr(attr, put1, put2, put3)

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
            cmds.layout(row3, e=True, m=val)

        row = cmds.rowLayout(nc=3, adj=2, cw2=[s.colWidth, s.colWidth], p=s.wrapper)
        # FROM COLUMN!
        cmds.columnLayout(adj=True, w=s.colWidth, p=row)
        objBtn = cmds.button(
            ann=s.i18n["fromDesc"],
            l=objDown,
            h=s.rowHeight,
            bgc=[0.3,0.3,0.3],
            c=lambda x: sync()
        )
        row1 = cmds.columnLayout(adj=True, m=False)
        # ARROW
        cmds.columnLayout(adj=True, p=row)
        cmds.text(
            l="  >  ",
            h=s.rowHeight,
            )
        row2 = cmds.columnLayout(adj=True, m=False)
        # TO COLUMN
        cmds.columnLayout(adj=True, w=s.colWidth, p=row)
        btn = cmds.button(
            ann=s.i18n["toDesc"],
            l=obj,
            h=s.rowHeight,
            c=lambda x: warn.run(s.performObjRetarget, obj, btn)
            )
        row3 = cmds.columnLayout(adj=True, m=False)
        return row1, row2, row3

    def addAttr(s, attr, parent1, parent2, parent3):
        # Insert FROM
        cmds.text(
            l=attr,
            h=s.rowHeight,
            p=parent1
            )
        # Insert ARROW
        cmds.text(
            l="  >  ",
            h=s.rowHeight,
            p=parent2
            )
        # Insert To
        btn = cmds.button(
            ann=s.i18n["toDesc"],
            l=attr,
            h=s.rowHeight,
            p=parent3,
            c=lambda x: warn.run(s.performAttrRetarget, attr, btn)
            )
    def performObjRetarget(s, old, element):
        selection = cmds.ls(sl=True, type="transform")
        if len(selection) == 1:
            sel = selection[0]
            if sel not in s.allItems:
                # TODO!!
                # WHAT IF THE NEW OBJECT HAS DIFFERENT ATTRIBUTES?
                # Are we really just re-referencing a name?
                # Answer, replace the whole object each time.
                # If one attribute changes, replace the whole thing anyway?
                # ASK TO CONFIRM FIRST!!
                ans = cmds.confirmDialog(
                    t=s.i18n["confirm"],
                    m=s.i18n["targetConfirm"],
                    button=[s.i18n["yes"], s.i18n["no"]],
                    defaultButton=s.i18n["yes"],
                    cancelButton=s.i18n["no"],
                    dismissString=s.i18n["no"]
                    )
                if ans == s.i18n["yes"]: # Are we ok to delete??
                    attrs = cmds.listAttr(sel, k=True)
                    print "Retargeting %s to %s" % (old, sel)
                    s.sendRetarget(s.char, old, sel)
                    cmds.button(element, e=True, l=sel)
            else:
                raise RuntimeError, "The selected object is already assigned."
        else:
            raise RuntimeError, "You must select a single object."

    def performAttrRetarget(s, old, element):
        selection = cmds.ls(sl=True, type="transform")
        if len(selection) == 1:
            sel = selection[0]
            # Get attributes selected!
            attr = [cmds.attributeQuery(at, n=sel, ln=True) for at in cmds.channelBox('mainChannelBox', sma=True, q=True)]
            if len(attr) == 1:
                at = attr[0]
                if at not in s.allItems:
                    # ASK TO CONFIRM FIRST!!
                    ans = cmds.confirmDialog(
                        t=s.i18n["confirm"],
                        m=s.i18n["targetConfirm"],
                        button=[s.i18n["yes"], s.i18n["no"]],
                        defaultButton=s.i18n["yes"],
                        cancelButton=s.i18n["no"],
                        dismissString=s.i18n["no"]
                        )
                    if ans == s.i18n["yes"]: # Are we ok to retarget??
                        print "Retargeting %s to %s" % (old, at)
                        s.sendRetarget(s.char, old, at)
                        cmds.button(element, e=True, l=at)
                        return
                else:
                    raise RuntimeError, "The selected Attribute is already assigned."
        raise RuntimeError, "You must select a single attribute."

    def save(s):
        s.char.save()
