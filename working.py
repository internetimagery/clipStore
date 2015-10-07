
import maya.cmds as cmds

i18n = {
    "characterNew"  : {
        "title"     : "Create a new Character"
    }
}

class CharacterNew(object):
    """
    Create a new character gui
    """
    def __init__(s, i18n):
        s.i18n = i18n
        winName = "CharacterNewWin"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.window = cmds.window(t=s.i18n["title"], rtf=True)
        cmds.columnLayout(adj=True)
        cmds.text("here")
        cmds.showWindow(s.window)
