# Create a new/edit clip

import maya.cmds as cmds
import time

class ClipEdit(object):
    """
    Create or edit an Animation
    """
    def __init__(s, i18n, requestThumb, sendInfo):
        s.i18n = i18n
        s.requestThumb = requestThumb # asking for new thumbnail
        s.sendInfo = sendInfo # replying with save data
        s.data = {}

        s.camName = "TempCam_%s" % int(time.time())
        s.createCam()

        s.winName = "AnimNewWin"
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t=s.i18n["title"])
        mainLayout = cmds.columnLayout()
        ## CAMERA CONTROLS
        s.live = True # Live cam?
        s.camLayout = cmds.paneLayout(h=500, w=500, p=mainLayout)
        viewer = cmds.modelPanel(
            menuBarVisible=False,
            camera=s.camera,
            )
        cmds.modelEditor( # Tweak nice default visuals
            viewer,
            e=True,
            grid=False,
            da="smoothShaded",
            allObjects=False,
            nurbsSurfaces=True,
            polymeshes=True,
            subdivSurfaces=True,
            displayTextures=True
            )
        s.previewLayout = cmds.columnLayout(
            h=500,
            w=500,
            p=mainLayout,
            m=False
            )
        s.preview = cmds.iconTextStaticLabel(
            style="iconOnly",
            h=500,
            w=500,
            bgc=[0.2,0.2,0.2],
            image="out_snapshot.png"
        )
        cmds.columnLayout(adj=True, p=mainLayout)
        cmds.separator()
        ## DATA CONTROLS
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
            l=s.i18n["captureBtn"],
            ann=s.i18n["thumbDesc"],
            style="iconAndTextVertical",
            h=90,
            w=90,
            bgc=[0.2,0.2,0.2],
            image="out_snapshot.png",
            c=s.capture
        )
        cmds.showWindow(s.window)
        cmds.scriptJob(uid=[s.window, s.cleanup], ro=True)

    def capture(s): # Ask for captures
        if s.live:
            s.live = False
            cmds.layout(s.camLayout, e=True, m=False)
            cmds.layout(s.previewLayout, e=True, m=True)
            cmds.iconTextButton(s.thumb, e=True, l=s.i18n["recaptureBtn"])
        else:
            s.live = True
            cmds.layout(s.previewLayout, e=True, m=False)
            cmds.layout(s.camLayout, e=True, m=True)
            cmds.iconTextButton(s.thumb, e=True, l=s.i18n["captureBtn"])

    def createCam(s):
        if not cmds.objExists(s.camName):
            s.camera = cmds.camera(n=s.camName)[0]
        else:
            s.camera = cmds.ls(s.camName)[0]
        cmds.viewSet(s.camera, p=True) # Move camera to perspective position
        cmds.setAttr("%s.focalLength" % s.camera, 500)
        cmds.setAttr("%s.horizontalFilmAperture" % s.camera, 5)
        cmds.setAttr("%s.verticalFilmAperture" % s.camera, 5)
        cmds.setAttr("%s.visibility" % s.camera, 0)

    def cleanup(s):
        # Remove temporary camera
        if cmds.objExists(s.camera):
            cmds.delete(s.camera)

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

from animCopy.i18n.en import En as i18n

def test(*arg):
    print arg

ClipNew(i18n["clipNew"], test, test)
