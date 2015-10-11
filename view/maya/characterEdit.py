# Edit the character

import maya.cmds as cmds
import animCopy.view.maya.warn as warn

i18n = {
    "characterEdit" : {
        "title"         : "Editing Character",
        "addBtn"        : "Add selected Objects",
        "retargetBtn"   : "Retarget Objects",
        "filter"        : "Filter attributes",
        "attrs"         : "Include / Exclude objects and attributes",
        "confirm"       : "Please confirm...",
        "delDesc"       : "Remove object from Character.\nBE CAREFULL, this could break Clips.",
        "delConfirm"    : "Are you sure you wish to delete this?\nIf you are replacing it with a nother object, consider Retargeting.",
        "yes"           : "Yes",
        "no"            : "No"
    }
}

class CharacterEdit(object):
    def __init__(s, i18n, char, requestObjects, sendNewObj, sendAttributeChange, sendObjDelete):
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
            c=lambda: warn.run(s.refresh, s.sendSelection())
        )
        cmds.iconTextButton(
            l=s.i18n["retargetBtn"],
            image="geometryToBoundingBox.png",
            style="iconAndTextHorizontal",
            c=lambda: ""
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
        data = s.requestObjects()
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
            s.sendObjDelete(obj)

    def sendSelection(s):
        """
        Send new objects from selected objects
        """
        selection = cmds.ls(sl=True, type="transform")
        if selection:
            store = {}
            for sel in selection:
                store[sel] = cmds.listAttr(sel, k=True)
            s.sendNewObj(store)
        else: raise RuntimeError, "Nothing selected."

    def addAttr(s, val, attr, obj, parent):
        def boxChange(attr, val):
            s.sendAttributeChange(val, attr, obj)
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
        cmds.iconTextStaticLabel(
            l="",
            style="iconOnly",
            image="cube.png",
            h=20,
            w=20,
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
            ofc=lambda x: warn.run(s.refresh, s.sendAttributeChange(x, attr))
        )
    def save(s):
        s.char.save()

import os.path
import animCopy.character
path = "/home/maczone/Desktop/something.zip"

class test(object):
    def __init__(s, char):
        s.char = char
        s.char.metadata["filters"] = s.char.metadata.get("filters", [])

    def sendCharData(s):
        """
        Prep data, replacing references with real names.
        Data = { object : { attribute : True/False } }
        """
        return dict((s.char.ref[a], dict((s.char.ref[c], d) for c, d in b.items())) for a, b in s.char.data.items())

    def addObjects(s, objects):
        """
        Add selected objects to character
        Get selection should return { obj : [ attribute1, attribute2, ... ] }
        """
        if objects:
            # Grab all inactive attributes so we can skip them in the adding process
            exclusions = set([c for a, b in s.char.data.items() for c, d in b.items() if not d])
            # Create new entry
            new = dict((s.char.ref[a], dict((s.char.ref[c], False if s.char.ref[c] in exclusions else True) for c in b)) for a, b in objects.items())
            # Add entry to existing data
            s.char.data = dict(s.char.data, **new)
        else: raise RuntimeError, "Nothing selected."

    def removeObject(s, obj):
        """
        Remove a given object.
        """
        obj = s.char.ref[obj]
        if obj in s.char.data:
            del s.char.data[obj]
        else:
            raise RuntimeError, "Object not in collection."

    def editAttrs(s, enable, attr, obj=None):
        """
        Enable or Disable attributes.
        If no object is specified. Change in bulk.
        """
        attr = s.char.ref[attr]
        obj = s.char.ref[obj] if obj else None
        for o, attrs in s.char.data.items():
            if not obj or o == obj:
                for at in attrs:
                    if at == attr:
                        s.char.data[o][at] = enable

c = animCopy.character.Character(path, "maya")
t = test(c)

CharacterEdit(
    i18n["characterEdit"],
    c,
    t.sendCharData,
    t.addObjects,
    t.editAttrs,
    t.removeObject
    )
