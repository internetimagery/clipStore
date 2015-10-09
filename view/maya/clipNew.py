# Create a new clip

import maya.cmds as cmds

class ClipNew(object):
    """
    Create or edit an Animation
    """
    def __init__(s, i18n, requestThumb, sendInfo, overrides=None):
        s.i18n = i18n
        s.requestThumb = requestThumb # asking for new thumbnail
        s.sendInfo = sendInfo # replying with save data
        s.data = overrides.copy() if overrides else {}
        s.winName = "AnimNewWin"
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t=s.i18n["title"])
        cmds.columnLayout(adj=True)
        cmds.rowLayout(nc=2, adj=1)
        cmds.columnLayout(adj=True)
        s.clipname = cmds.textFieldGrp(
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
            image=s.data.get("thumb", "out_snapshot.png"),
            c=s.updateThumb
        )
        cmds.setParent("..")
        cmds.rowLayout(nc=3, adj=1)
        cmds.separator()
        cmds.button(
            l=s.i18n["save"],
            bgc=[0.4,0.6,0.5],
            c=lambda x: s.save(),
            h=40
            )
        cmds.button(
            l=s.i18n["cancel"],
            bgc=[0.6,0.3,0.3],
            c=lambda x: cmds.deleteUI(s.window),
            h=40
            )
        cmds.showWindow(s.window)
    def updateThumb(s):
        thumb = s.requestThumb()
        if thumb:
            s.data["thumb"] = thumb
            cmds.iconTextButton(
                s.thumb,
                e=True,
                image=thumb
            )
    def save(s):
        # Validate inputs
        clipname = cmds.textFieldGrp(s.clipname, q=True, tx=True).strip()
        if cmds.checkBoxGrp(s.clippose, q=True, v1=True):
            frame = cmds.currentTime(q=True)
            cliprange = [frame, frame]
        else:
            v1 = cmds.intFieldGrp(s.cliprange, q=True, v1=True)
            v2 = cmds.intFieldGrp(s.cliprange, q=True, v2=True)
            cliprange = sorted([v1, v2])
        if clipname:
            if s.data.has_key("thumb"):
                s.data = {
                    "clipname" : clipname,
                    "cliprange": cliprange
                }
                s.sendInfo(s.data)
                cmds.deleteUI(s.window)
            else:
                cmds.confirmDialog(t="oops", m="Missing a clip image.")
        else:
            cmds.confirmDialog(t="oops", m="Missing a clip name.")
