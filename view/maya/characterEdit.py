# Edit the character

import maya.cmds as cmds
import animCopy.view.maya.warn as warn

i18n = {
    "characterEdit" : {
        "title"     : "Editing Character",
        "addBtn"    : "Add selected Objects",
        "filter"    : "Filter attributes",
        "attrs"     : "Include / Exclude objects and attributes",
        "retarget"  : "Retarget objects and attributes.",
        "retargetDesc": "If the objects or attributes have changed names,\nyou change swap the exsiting object for the new one."
    }
}

class CharacterEdit(object):
    def __init__(s, i18n, char, requestObjAdd, requestObjects, sendAttributeChange):
        s.i18n = i18n
        s.char = char
        s.requestObjects = requestObjects
        s.sendAttributeChange = sendAttributeChange
        name = s.char.metadata["name"].title()

        s.objClose = {} # Close state of obj
        s.filterBox = {} # Storing filter bloxes for dynamic updates

        winName = "CharacterEditWin"
        if cmds.window(winName, ex=True): cmds.deleteUI(winName)
        s.window = cmds.window(t="%s :: %s" % (s.i18n["title"], name), rtf=True)
        cmds.columnLayout(adj=True)
        # Top button
        cmds.iconTextButton(
            l=s.i18n["addBtn"],
            image="selectByObject.png",
            style="iconAndTextHorizontal",
            h=30,
            c=lambda: s.refresh(warn.run(requestObjAdd))
        )
        cmds.separator()
        row = cmds.rowLayout(nc=3, adj=2)
        # Begin Filters
        cmds.columnLayout(adj=True)
        cmds.text(l=i18n["filter"])
        cmds.separator()
        s.filterWrapper = cmds.scrollLayout(h=400, cr=True, bgc=[0.2,0.2,0.2])
        # Begin Objects
        cmds.columnLayout(adj=True, p=row)
        cmds.text(l=i18n["attrs"])
        cmds.separator()
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
                    s.addObj(attrs, obj)
                    for attr, val in attrs.items():
                        attrFilter.add(attr)

            if attrFilter:
                for attr in attrFilter:
                    s.addAttrFilter(attr, False if attr in exclusions else True)
    def addAttr(s, val, attr, obj):
        def boxChange(attr, val):
            s.sendAttributeChange(val, attr, obj)
            if val: cmds.checkBox(s.filterBox[attr], e=True, v=True)
        cmds.checkBox(
            l=attr,
            v=val,
            cc=lambda x: boxChange(attr, x)
            )
    def addObj(s, attrs, obj):
        print s.objClose
        def changeObj(obj, val):
            s.objClose[obj] = val
        s.objClose[obj] = s.objClose.get(obj, True)
        row = cmds.rowLayout(nc=2, adj=2, p=s.objWrapper)
        cmds.columnLayout(adj=True)
        cmds.button(l="del")
        cmds.frameLayout(
            l=obj,
            cll=True,
            cl=s.objClose[obj],
            cc=lambda: changeObj(obj, True),
            ec=lambda: changeObj(obj, False),
            p=row
            )
        for at, val in attrs.items():
            s.addAttr(val, at, obj)
    def addAttrFilter(s, attr, value):
        s.filterBox[attr] = cmds.checkBox(
            l=attr,
            v=value,
            p=s.filterWrapper,
            ofc=lambda x: s.refresh(s.sendAttributeChange(x, attr))
        )
    def save(s):
        s.char.save()

import os.path
import animCopy.character
import animCopy.model.maya as model
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

    def addSelection(s):
        """
        Add selected objects to character
        Get selection should return { obj : [ attribute1, attribute2, ... ] }
        """
        objs = model.selection().getSelection()
        if objs:
            # Grab all inactive attributes so we can skip them in the adding process
            exclusions = set([c for a, b in s.char.data.items() for c, d in b.items() if not d])
            # Create new entry
            new = dict((s.char.ref[a], dict((s.char.ref[c], False if s.char.ref[c] in exclusions else True) for c in b)) for a, b in objs.items())
            # Add entry to existing data
            s.char.data = dict(s.char.data, **new)
        else: raise RuntimeError, "Nothing selected."

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
    t.addSelection,
    t.sendCharData,
    t.editAttrs
    )
