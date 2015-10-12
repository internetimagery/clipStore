# Create a new/edit clip

import maya.cmds as cmds
import os.path
import time
import os

class ClipEdit(object):
    """
    Create or edit an Animation
    """
    def __init__(s, i18n, char, clip, previewImage, requestThumb):
        s.i18n = i18n
        s.char = char
        s.clip = clip
        s.previewImage = previewImage # Initial preview image
        s.requestThumb = requestThumb # asking for new thumbnail

        s.camName = "TempCam_%s" % int(time.time())
        s.createCam()

        # INIT DATA:
        clip.metadata["name"] = clip.metadata.get("name", "CLIP")
        clip.metadata["range"] = clip.metadata.get("range", [
            cmds.playbackOptions(q=True, min=True),
            cmds.playbackOptions(q=True, max=True)
            ])


        s.winName = "ClipNewWin"
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
            text=clip.metadata["name"],
            h=30,
            tcc=s.nameChange
        )

        r = clip.metadata["range"]
        s.clippose = cmds.checkBoxGrp(
            l=s.i18n["clippose"],
            h=30,
            v1=r[0] == r[1],
            cc=s.poseChange
            )
        s.cliprange = cmds.intFieldGrp(
            l=s.i18n["cliprange"],
            nf=2,
            v1=r[0],
            v2=r[1],
            en=False if cmds.checkBoxGrp(s.clippose, q=True, v1=True) else True,
            h=30,
            cc=s.rangeChange
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
            c=lambda: s.previewMode() if s.live else s.captureMode()
        )
        if s.previewImage:
            s.previewMode()
        else:
            s.captureMode()
        cmds.showWindow(s.window)
        cmds.scriptJob(uid=[s.window, s.save], ro=True)
        cmds.scriptJob(e=["quitApplication", s.cleanup], ro=True)

    def captureMode(s):
        s.live = True
        cmds.layout(s.previewLayout, e=True, m=False)
        cmds.layout(s.camLayout, e=True, m=True)
        cmds.iconTextButton(s.thumb, e=True, l=s.i18n["captureBtn"])

    def previewMode(s):
        s.live = True
        cmds.layout(s.previewLayout, e=True, m=False)
        cmds.layout(s.camLayout, e=True, m=True)
        cmds.iconTextButton(s.thumb, e=True, l=s.i18n["captureBtn"])
        cmds.iconTextStaticLabel(s.preview, e=True, image=s.previewImage.name if s.previewImage else "out_snapshot.png")

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

    def updateThumb(s):
        thumb = s.requestThumb()
        if thumb:
            s.clip.metadata["thumb"] = thumb
            cmds.iconTextButton(
                s.thumb,
                e=True,
                image=thumb
            )

    def nameChange(s, text):
        s.clip.metadata["name"] = text

    def poseChange(s, val):
        cmds.intFieldGrp(s.cliprange, e=True, en=False if val else True)
        frame = cmds.currentTime(q=True)
        clip.metadata["range"] = [frame, frame]

    def rangeChange(s):
        min_ = cmds.intFieldGrp(s.cliprange, q=True, v1=True)
        max_ = cmds.intFieldGrp(s.cliprange, q=True, v2=True)
        clip.metadata["range"] = sorted([min_, max_])

    def cleanup(s):
        # Remove temporary camera
        if cmds.objExists(s.camera):
            cmds.delete(s.camera)

    def save(s):
        s.char.save()

# from animCopy.i18n.en import En as i18n
#
# def test(*arg):
#     print arg
#
# ClipNew(i18n["clipNew"], test, test)
