# File dialog

import maya.cmds as cmds

class FileDialog(object):
    def load(s, i18n):
        f = cmds.fileDialog2(
            dir=cmds.workspace(q=True, rd=True),
            caption=i18n["titleLoad"],
            fileMode=1,
            okCaption=i18n["loadBtn"],
            cancelCaption=i18n["cancelBtn"],
            fileFilter="Character File (*.clips)"
        )
        return f[0] if f else None
    def save(s, i18n):
        f = cmds.fileDialog2(
            dir=cmds.workspace(q=True, rd=True),
            caption=i18n["titleSave"],
            fileMode=0,
            okCaption=i18n["saveBtn"],
            cancelCaption=i18n["cancelBtn"],
            fileFilter="Character File (*.clips)"
        )
        return f[0] if f else None
