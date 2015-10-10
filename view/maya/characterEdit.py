# Edit the character

# import maya.cmds as cmds

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
    def __init__(s, i18n, char, requestObjAdd):
        s.i18n = i18n
        s.char = char
        s.requestObjAdd = requestObjAdd # Validate selection
        name = s.char.metadata["name"].title()

        winName = "CharacterEdit%sWin" % name
        if cmds.window(winName, ex=True): cmds.deleteUI(winName)
        s.window = cmds.window(t="%s :: %s" % (s.i18n["title"], name), rtf=True)
        cmds.columnLayout(adj=True)
        # Top button
        cmds.button(
            l=i18n["addBtn"],
            h=40,
            c=lambda x: s.addSelected()
        )
        cmds.separator()
        row = cmds.rowLayout(nc=3, adj=2)
        # Begin Filters
        cmds.columnLayout(adj=True)
        cmds.text(l=i18n["filter"])
        cmds.separator()
        s.attrwrapper = cmds.scrollLayout(cr=True, bgc=[0.2,0.2,0.2])
        # Begin Objects
        cmds.columnLayout(adj=True, p=row)
        cmds.text(l=i18n["attrs"])
        cmds.separator()
        s.objwrapper = cmds.scrollLayout(cr=True, bgc=[0.2,0.2,0.2])
        # Begin retarget
        cmds.columnLayout(
            adj=True,
            p=row,
            ann=i18n["retargetDesc"])
        cmds.text(l=i18n["retarget"])
        cmds.separator()
        s.retargetwrapper = cmds.scrollLayout(cr=True, bgc=[0.2,0.2,0.2])
        cmds.showWindow(s.window)
        cmds.scriptJob(uid=[s.window, s.save], ro=True)
        s.refresh()
    def addSelected(s):
        with view.warn:
            s.requestObjAdd() # Add to the list of objects
    def refresh(s): # Build out GUI
        filterAtt = set()
        print s.char.data
        for obj in s.char.data:
            print obj
    def save(s):
        s.char.save()

import os.path
import animCopy.character
import animCopy.view.maya as view
import animCopy.model.maya as model
path = "/home/maczone/Desktop/something.char"

class test(object):
    def __init__(s, char):
        s.char = char
    def addSelection(s):
        """
        Add selected objects to character
        """
        objs = model.selection().getSelection()
        if objs:
            filters = s.char.metadata.get("filters", [])
            for obj in objs:
                for atr in objs[obj]:
                    objID = s.char.ref[obj]
                    atrID = s.char.ref[atr]
                    s.char.data[objID] = s.char.data.get(objID, {})
                    s.char.data[objID][atrID] = False if atr in filters else True
            return s.char.data
        else: raise RuntimeError, "Nothing selected."


c = animCopy.character.Character(path, "maya")
t = test(c)
CharacterEdit(i18n["characterEdit"], c, t.addSelection)

# objects, attributes in heirarchy
# filter for attributes
