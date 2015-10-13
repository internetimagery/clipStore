# Create a new/edit clip

from pprint import pprint
import maya.cmds as cmds
import os.path
import time
import warn
import os

class ClipEdit(object):
    """
    Create or edit an Animation
    """
    def __init__(s, i18n, char, clip, requestThumb, requestCharData, requestClipCapture):
        s.i18n = i18n
        s.char = char
        s.clip = clip
        s.requestThumb = requestThumb # asking for new thumbnail
        s.requestClipCapture = requestClipCapture # Grab capture information
        s.data = requestCharData(char) # Get data for clip
        s.thumbs = {} # Captured thumbs
        s.winWidth = 500 # Window width

        # VALIDATE BEFORE DOING ANYTHING
        with warn:
            s.validateObjs()

        s.camName = "TempCam_%s" % int(time.time())
        s.createCam()

        s.name = "CLIP"
        s.pose = True
        s.range = [
            cmds.playbackOptions(q=True, min=True),
            cmds.playbackOptions(q=True, max=True)
        ]

        s.winName = "ClipNewWin"
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t=s.i18n["title"])
        mainLayout = cmds.columnLayout()
        ## CAMERA CONTROLS
        s.camLayout = cmds.paneLayout(h=s.winWidth, w=s.winWidth, p=mainLayout)
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
        cmds.columnLayout(w=s.winWidth, p=mainLayout)
        cmds.separator()
        ## DATA CONTROLS
        cmds.columnLayout(adj=True)
        s.clipname = cmds.textFieldGrp(
            l=s.i18n["clipname"],
            text=s.name,
            h=30,
            tcc=s.nameChange
        )
        s.clippose = cmds.checkBoxGrp(
            l=s.i18n["clippose"],
            h=30,
            v1=True,
            cc=s.poseChange
            )
        s.cliprange = cmds.intFieldGrp(
            l=s.i18n["cliprange"],
            nf=2,
            v1=s.range[0],
            v2=s.range[1],
            en=False,
            h=30,
            cc=s.rangeChange
        )
        cmds.showWindow(s.window)
        cmds.scriptJob(uid=[s.window, s.save], ro=True)
    def validateObjs(s):
        for obj in s.data:
            if not cmds.objExists(obj):
                raise RuntimeError, "%s could not be found." % obj

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

    def nameChange(s, text):
        s.name = text

    def poseChange(s, val):
        cmds.intFieldGrp(s.cliprange, e=True, en=False if val else True)
        s.pose = val

    def rangeChange(s, min_, max_):
        # min_ = cmds.intFieldGrp(s.cliprange, q=True, v1=True)
        # max_ = cmds.intFieldGrp(s.cliprange, q=True, v2=True)
        s.range = sorted([min_, max_])

    def save(s):
        with warn:
            # Grab name
            s.clip.metadata["name"] = s.name
            # Grab Thumbnails
            s.clip.metadata = dict(s.clip.metadata, **s.requestThumb(s.camera))
            # Grab range information
            if s.pose:
                frame = cmds.currentTime(q=True)
                frameRange = [frame, frame]
            else:
                frameRange = s.range
            # # Grab Clip
            s.clip.clipData = s.requestClipCapture(s.data, frameRange)
            # Save information
            s.char.save()
            # Remove temporary camera
            if cmds.objExists(s.camera):
                cmds.delete(s.camera)
