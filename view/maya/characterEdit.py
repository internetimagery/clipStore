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
        data, filters = s.requestObjects()
        # Build GUI Elements
        print filters
        attrFilter = set() # Short list of all attributes.
        if data:
            for obj, attrs in data.items():
                for attr, val in attrs.items():
                    attrFilter.add(attr)

            if attrFilter:
                for attr in attrFilter:
                    s.addAttrFilter(attr, False if attr in filters else True)
    def addAttrFilter(s, attr, value):
        cmds.checkBox(
            l=attr,
            v=value,
            p=s.filterWrapper,
            cc=lambda x: s.sendFilterUpdate(attr, x)
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
        Send character data replacing ID with real names,
        and a short list of filters.
        Data = { object : { attribute : True/False } }
        Filters = [filter1, filter2, ... ]
        """
        def addAttr(attr):
            attrID = s.char.ref[attr]
            if attr in s.char.metadata["filters"]:
                filteredAttr.add(attrID)
            return attrID
        filteredAttr = set()
        data = {}
        if s.char.data:
            data = dict((s.char.ref[a], dict((addAttr(c), d) for c, d in b.items())) for a, b in s.char.data.items())
        return data, list(filteredAttr)

    def addSelection(s):
        """
        Add selected objects to character
        Get selection should return { obj : { attribute : None } }
        """
        objs = model.selection().getSelection()
        from pprint import pprint
        pprint(s.char.data)
        if objs:
            filters = s.char.metadata.get("filters", [])
            new = dict((s.char.ref[a], dict((s.char.ref[c], False if d in filters else True) for c, d in b.items())) for a, b in objs.items())
            s.char.data = dict(s.char.data, **new)
        else: raise RuntimeError, "Nothing selected."

    def addRemoveFilters(s, filterName, include):
        """
        Add or Remove a filter. A shortcut to block out chunks of attributes.
        Filters actually saved are the inverse of what you'd consider normal.
        Not having a filter in the list is the same as having it "on".
        """
        filterID = s.char.ref[filterName]
        if filterID in s.char.metadata["filters"]:
            if include:
                s.char.metadata["filters"].remove(filterID)
        else:
            if not include:
                s.char.metadata["filters"].append(filterID)



c = animCopy.character.Character(path, "maya")
t = test(c)
# print t.sendCharData()
CharacterEdit(
    i18n["characterEdit"],
    c,
    t.addSelection,
    t.sendCharData,
    t.addRemoveFilters
    )
