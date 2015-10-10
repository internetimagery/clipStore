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
    def __init__(s, i18n, char):
        s.i18n = i18n
        s.char = char
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
    def addSelected(s):
        try:
            sel = cmds.ls(sl=True, type="transform")
            if sel:
                pass
            else: raise RuntimeError, "You need to select something. :)"
        except RuntimeError as e:
            cmds.confirmDialog(t="Oh no...", m=str(e))

    def save(s):
        s.char.save()

import os.path
import animCopy.character
path = "/home/maczone/Desktop/something.char"

c = animCopy.character.Character(path, "maya")
CharacterEdit(i18n["characterEdit"], c)

# objects, attributes in heirarchy
# filter for attributes
