# Edit the character

import maya.cmds as cmds
import warn

class CharacterEdit(object):
    def __init__(s, i18n, char, requestRetarget, requestObjects, sendNewObj, sendAttributeChange, sendObjDelete):
        s.i18n = i18n
        s.char = char
        s.requestObjects = requestObjects
        s.sendNewObj = sendNewObj
        s.sendAttributeChange = sendAttributeChange
        s.sendObjDelete = sendObjDelete
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
        cmds.rowLayout(nc=2)
        cmds.iconTextButton(
            l=s.i18n["addBtn"],
            image="selectByObject.png",
            style="iconAndTextHorizontal",
            c=lambda: s.refresh(warn.run(s.sendSelection)
        )
        cmds.iconTextButton(
            l=s.i18n["retargetBtn"],
            image="geometryToBoundingBox.png",
            style="iconAndTextHorizontal",
            c=lambda: (warn.run(requestRetarget, s.char), cmds.deleteUI(s.window))
        )
        cmds.setParent("..")
        cmds.separator()
        row = cmds.rowLayout(nc=3, adj=2)
        # Begin Filters
        cmds.columnLayout(adj=True)
        cmds.text(l=i18n["filter"])
        s.filterWrapper = cmds.scrollLayout(h=400, cr=True, bgc=[0.2,0.2,0.2])
        # Begin Objects
        cmds.columnLayout(adj=True, p=row)
        cmds.text(l=i18n["attrs"])
        s.objWrapper = cmds.scrollLayout(h=400, cr=True, bgc=[0.2,0.2,0.2])
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
        s.clear(s.filterWrapper)
        s.clear(s.objWrapper)
        s.filterBox = {}
        # Get data to build
        data = s.requestObjects(s.char)
        # Create list of exclusions
        exclusions = set([c for a, b in data.items() for c, d in b.items() if not d])
        attrFilter = set() # Short grab all elements
        if data:
            for obj, attrs in data.items():
                if attrs:
                    # Object / Attributes
                    atPoint = s.addObj(obj) # Build object. Return position for attributes
                    for attr, val in attrs.items():
                        attrFilter.add(attr)
                        s.addAttr(val, attr, obj, atPoint)
            if attrFilter:
                attrFilter = sorted(list(attrFilter))
                for attr in attrFilter:
                    s.addAttrFilter(attr, False if attr in exclusions else True)
    def askDeleteObj(s, obj):
        """
        Ask for permission to delete object. Big deal!!
        """
        ans = cmds.confirmDialog(
            t=s.i18n["confirm"],
            m=s.i18n["delConfirm"],
            button=[s.i18n["yes"], s.i18n["no"]],
            defaultButton=s.i18n["yes"],
            cancelButton=s.i18n["no"],
            dismissString=s.i18n["no"]
            )
        if ans == s.i18n["yes"]: # Are we ok to delete??
            s.sendObjDelete(s.char, obj)

    def sendSelection(s):
        """
        Send new objects from selected objects
        """
        selection = cmds.ls(sl=True, type="transform")
        if selection:
            store = {}
            for sel in selection:
                store[sel] = cmds.listAttr(sel, k=True)
            s.sendNewObj(s.char, store)
        else: raise RuntimeError, "Nothing selected."

    def addAttr(s, val, attr, obj, parent):
        def boxChange(attr, val):
            s.sendAttributeChange(s.char, val, attr, obj)
            if val: cmds.checkBox(s.filterBox[attr], e=True, v=True)
        cmds.checkBox(
            l=attr,
            v=val,
            cc=lambda x: warn.run(boxChange, attr, x),
            p=parent
            )
    def addObj(s, obj):
        def changeObj(obj, val):
            s.objClose[obj] = val
        s.objClose[obj] = s.objClose.get(obj, True)
        row = cmds.rowLayout(nc=3, adj=2, p=s.objWrapper)
        # ICON
        cmds.iconTextButton(
            l="",
            style="iconOnly",
            image="cube.png",
            h=20,
            w=20,
            c=warn.run(cmds.select, obj, r=True)
            p=row
        )
        # OBJECT
        attrPoint = cmds.frameLayout(
            l=obj,
            cll=True,
            cl=s.objClose[obj],
            cc=lambda: warn.run(changeObj, obj, True),
            ec=lambda: warn.run(changeObj, obj, False),
            bgc=[0.3,0.3,0.3],
            p=row
            )
        # DELETE BUTTON
        cmds.iconTextButton(
            ann=s.i18n["delDesc"],
            image="removeRenderable.png",
            style="iconOnly",
            h=20,
            w=20,
            p=row,
            c=lambda: warn.run(s.refresh, s.askDeleteObj(obj))
        )
        return attrPoint
    def addAttrFilter(s, attr, value):
        s.filterBox[attr] = cmds.checkBox(
            l=attr,
            v=value,
            p=s.filterWrapper,
            ofc=lambda x: warn.run(s.refresh, s.sendAttributeChange(s.char, x, attr))
        )
    def save(s):
        s.char.save()
