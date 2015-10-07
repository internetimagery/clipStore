
i18n = {
    "animNew"   : {
        "title"         : "Create a new clip.",
        "clipname"      : "Name your clip",
        "clippose"      : "Create a single pose",
        "cliprange"     : "Insert framerange for clip",
        "thumbNew"      : "Capture a new thumbnail",
        "thumbDesc"     : "Click to create a new thumbnail"
    }
}

import maya.cmds as cmds

class AnimNew(object):
    """
    Create or edit an Animation
    """
    def __init__(s, i18n, overrides=None):
        s.i18n = i18n
        s.data = overrides if overrides else {}
        s.winName = "AnimNewWin"
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t=s.i18n["title"])
        cmds.columnLayout(adj=True)
        cmds.rowLayout(nc=2, adj=1)
        cmds.columnLayout(adj=True)
        cmds.textFieldGrp(
            l=s.i18n["clipname"],
            text=s.data.get("clipname", ""),
            h=30
        )
        r = s.data.get("cliprange", [
            cmds.playbackOptions(q=True, min=True),
            cmds.playbackOptions(q=True, max=True)
            ])
        s.clippose = cmds.checkBoxGrp(
            l=s.i18n["clippose"],
            h=30,
            v1=r[0] == r[1],
            cc= lambda x: cmds.intFieldGrp(s.cliprange, e=True, en=False if x else True)
        )
        s.cliprange = cmds.intFieldGrp(
            l=s.i18n["cliprange"],
            nf=2,
            v1=r[0],
            v2=r[1],
            en=False if cmds.checkBoxGrp(s.clippose, q=True, v1=True) else True,
            h=30
        )
        cmds.setParent("..")
        s.thumb = cmds.iconTextButton(
            l=s.i18n["thumbNew"],
            ann=s.i18n["thumbDesc"],
            style="iconOnly",
            h=90,
            w=90,
            bgc=[0.2,0.2,0.2],
            image=s.data.get("thumb", "out_snapshot.png")
        )
        cmds.showWindow(s.window)

AnimNew(i18n["animNew"])
