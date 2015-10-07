# Save Characters as files. Clips within the file


import maya.cmds as cmds

i18n = {
    "characterNew"  : {
        "title"     : "Create a new Character",
        "whitelist" : "Whitelist Filter",
        "blacklist" : "Blacklist Filter"
    }
}

class CharacterNew(object):
    """
    Create a new character gui
    """
    def __init__(s, i18n, overrides=None):
        s.i18n = i18n
        s.data = overrides.copy() if overrides else {}
        winName = "CharacterNewWin"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.window = cmds.window(t=s.i18n["title"], rtf=True)
        cmds.columnLayout(adj=True)
        cmds.tabLayout(cr=True)
        cmds.scrollLayout(s.i18n["whitelist"])
        cmds.text("here")
        cmds.setParent("..")
        cmds.scrollLayout(s.i18n["blacklist"])
        cmds.text("here2")
        cmds.showWindow(s.window)

CharacterNew(i18n["characterNew"])
