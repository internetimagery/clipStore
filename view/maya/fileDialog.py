# File dialog

import maya.cmds as cmds

class FileDialog(object):
    def __init__(s, i18n):
        s.i18n = i18n
    def openDir(s):
        f = cmds.fileDialog2(
            dir=cmds.workspace(q=True, rd=True),
            caption=s.i18n["filedialog.openDir"],
            fileMode=3,
            okCaption=s.i18n["filedialog.openDir"],
            cancelCaption=s.i18n["cancel"],
            fileFilter="Character File (*.char)"
        )
        return f[0] if f else None
    def load(s):
        f = cmds.fileDialog2(
            dir=cmds.workspace(q=True, rd=True),
            caption=s.i18n["filedialog.titleLoad"],
            fileMode=1,
            okCaption=s.i18n["filedialog.loadBtn"],
            cancelCaption=s.i18n["cancel"],
            fileFilter="Character File (*.char)"
        )
        return f[0] if f else None
    def save(s):
        f = cmds.fileDialog2(
            dir=cmds.workspace(q=True, rd=True),
            caption=s.i18n["filedialog.titleSave"],
            fileMode=0,
            okCaption=s.i18n["filedialog.saveBtn"],
            cancelCaption=s.i18n["cancel"],
            fileFilter="Character File (*.char)"
        )
        return f[0] if f else None
