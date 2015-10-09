# File dialog

import maya.cmds as cmds

class FileDialog(object):
    def __init__(s, i18n):
        s.i18n = i18n
    def openDir(s):
        f = cmds.fileDialog2(
            dir=cmds.workspace(q=True, rd=True),
            caption=s.i18n["openDir"],
            fileMode=3,
            okCaption=s.i18n["openDir"],
            cancelCaption=s.i18n["cancelBtn"],
            fileFilter="Character File (*.char)"
        )
        return f[0] if f else None
    def load(s):
        f = cmds.fileDialog2(
            dir=cmds.workspace(q=True, rd=True),
            caption=s.i18n["titleLoad"],
            fileMode=1,
            okCaption=s.i18n["loadBtn"],
            cancelCaption=s.i18n["cancelBtn"],
            fileFilter="Character File (*.char)"
        )
        return f[0] if f else None
    def save(s):
        f = cmds.fileDialog2(
            dir=cmds.workspace(q=True, rd=True),
            caption=s.i18n["titleSave"],
            fileMode=0,
            okCaption=s.i18n["saveBtn"],
            cancelCaption=s.i18n["cancelBtn"],
            fileFilter="Character File (*.char)"
        )
        return f[0] if f else None
