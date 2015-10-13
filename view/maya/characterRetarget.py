# Retarget character names
# Created 12/10/15 Jason Dixon
# http://internetimagery.com


import maya.cmds as cmds
import warn

class CharacterRetarget(object):
    def __init__(s, i18n, char, requestEdit, requestObjects, sendRetarget):
        s.i18n = i18n
        s.char = char
        s.requestObjects = requestObjects
        s.sendRetarget = sendRetarget
        name = s.char.metadata["name"].title()

        s.colWidth = 300
        s.rowHeight = 30

        winName = "CharacterEditWin"
        if cmds.window(winName, ex=True): cmds.deleteUI(winName)
        s.window = cmds.window(t="%s :: %s" % (s.i18n["characterRetarget.title"], name), rtf=True)
        cmds.columnLayout(adj=True)
        # Title
        cmds.text(l="<h1>%s</h1>" % name)
        # Top button
        cmds.iconTextButton(
            l=s.i18n["characterRetarget.return"],
            image="goToBindPose.png",
            style="iconAndTextHorizontal",
            c=lambda: warn.run(requestEdit, s.char)
        )
        cmds.separator()
        cmds.rowLayout(nc=3, adj=2)
        cmds.text(l=i18n["characterRetarget.from"], w=s.colWidth)
        cmds.text(l="  >  ", h=s.rowHeight)
        cmds.text(l=i18n["characterRetarget.to"], w=s.colWidth)
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
            attributes = set()
            for obj in sorted(data.keys()):
                attrs = data[obj]
                if attrs:
                    attributes = set()
                    # Put in some objects
                    s.allItems.add(obj)
                    s.addPair(obj, s.performObjRetarget)
                    for attr in attrs:
                        attributes.add(attr)
                        s.allItems.add(attr)
            if attributes:
                cmds.columnLayout(adj=True, p=s.wrapper)
                cmds.separator()
                for at in sorted(list(attributes)):
                    s.addPair(at, s.performAttrRetarget)

    def addPair(s, item, func):
        row = cmds.rowLayout(nc=3, adj=2, cw2=[s.colWidth, s.colWidth], p=s.wrapper)
        # FROM COLUMN!
        cmds.text(
            ann=s.i18n["characterRetarget.fromDesc"],
            l=item,
            h=s.rowHeight,
            w=s.colWidth,
            bgc=[0.3,0.3,0.3],
            )
        cmds.text(
            l="  >  ",
            h=s.rowHeight,
            )
        btn = cmds.button(
            ann=s.i18n["characterRetarget.toDesc"],
            l=item,
            h=s.rowHeight,
            c=lambda x: warn.run(func, item, btn),
            w=s.colWidth,
            )

    def performObjRetarget(s, old, element1):
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
                    t=s.i18n["characterRetarget.confirm"],
                    m=s.i18n["characterRetarget.targetConfirm"],
                    button=[s.i18n["yes"], s.i18n["no"]],
                    defaultButton=s.i18n["yes"],
                    cancelButton=s.i18n["no"],
                    dismissString=s.i18n["no"]
                    )
                if ans == s.i18n["yes"]: # Are we ok to delete??
                    attrs = cmds.listAttr(sel, k=True)
                    print "Retargeting %s to %s" % (old, sel)
                    s.sendRetarget(s.char, old, sel)
                    cmds.button(element1, e=True, l=sel)
            else:
                raise RuntimeError, "The selected object is already assigned."
        else:
            raise RuntimeError, "You must select a single object."

    def performAttrRetarget(s, old, element1):
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
                        t=s.i18n["characterRetarget.confirm"],
                        m=s.i18n["characterRetarget.targetConfirm"],
                        button=[s.i18n["yes"], s.i18n["no"]],
                        defaultButton=s.i18n["yes"],
                        cancelButton=s.i18n["no"],
                        dismissString=s.i18n["no"]
                        )
                    if ans == s.i18n["yes"]: # Are we ok to retarget??
                        print "Retargeting %s to %s" % (old, at)
                        s.sendRetarget(s.char, old, at)
                        cmds.button(element1, e=True, l=at)
                        return
                else:
                    raise RuntimeError, "The selected Attribute is already assigned."
        raise RuntimeError, "You must select a single attribute."

    def save(s):
        with warn:
            s.char.save()
