# Edit the character

import maya.cmds as cmds
import animCopy.view.maya.warn as warn

i18n = {
    "characterEdit" : {
        "title"     : "Editing Character",
        "addBtn"    : "Add selected Objects",
        "filter"    : "Filter attributes",
        "attrs"     : "Add objects and attributes",
        "retarget"  : "Retarget objects and attributes.",
        "retargetDesc": "If the objects or attributes have changed names,\nyou change swap the exsiting object for the new one."
    }
}

class CharacterEdit(object):
    def __init__(s, i18n, char, requestObjAdd, requestObjects, sendFilterUpdate):
        s.i18n = i18n
        s.char = char
        s.requestObjects = requestObjects
        s.sendFilterUpdate = sendFilterUpdate
        name = s.char.metadata["name"].title()

        winName = "CharacterEditWin"
        if cmds.window(winName, ex=True): cmds.deleteUI(winName)
        s.window = cmds.window(t="%s :: %s" % (s.i18n["title"], name), rtf=True)
        cmds.columnLayout(adj=True)
        # Top button
        cmds.button(
            l=i18n["addBtn"],
            h=40,
            c=lambda x: s.refresh(warn.run(requestObjAdd))
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
        # Begin retarget
        cmds.columnLayout(
            adj=True,
            p=row,
            ann=i18n["retargetDesc"])
        cmds.text(l=i18n["retarget"])
        cmds.separator()
        s.retargetWrapper = cmds.scrollLayout(h=400, cr=True, bgc=[0.2,0.2,0.2])
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
        s.clear(s.retargetWrapper)
        s.clear(s.filterWrapper)
        s.clear(s.objWrapper)
        # Get data to build
        data = s.requestObjects()
        # Create list of exclusions
        exclusions = set([c for a, b in data.items() for c, d in b.items() if not d])
        attrFilter = set() # Short grab all elements
        if data:
            for obj, attrs in data.items():
                for attr, val in attrs.items():
                    attrFilter.add(attr)

            if attrFilter:
                for attr in attrFilter:
                    s.addAttrFilter(attr, False if attr in exclusions else True)
    def addAttrFilter(s, attr, value):
        cmds.checkBox(
            l=attr,
            v=value,
            p=s.filterWrapper,
            cc=lambda x: s.sendFilterUpdate(x, attr)
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
