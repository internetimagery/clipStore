# Capture an image window

import maya.cmds as cmds

class ThumbNew(object):
    def __init__(s, i18n, callback):
        """
        Create a new thumbnail GUI
        """
        s.i18n = i18n
        s.callback = callback
        s.camName = "TempCam_%s" % int(time.time())
        s.camera = None
        s.createCam() # Create a temporary camera
        winName = "ThumbNEW"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.window = cmds.window(winName, t=i18n["title"], rtf=True)
        mainLayout = cmds.columnLayout(adj=True)
        # # Add Our capture frame
        cmds.paneLayout(h=500, w=500, p=mainLayout)
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
        cmds.columnLayout(adj=True, p=mainLayout)
        cmds.separator()
        cmds.iconTextButton(
            label=i18n["captureBtn"],
            style="iconAndTextVertical",
            font="boldLabelFont",
            image="rvSnapshot.png",
            height=50,
            bgc=[0.3,0.6,0.35],
            c=s.capture
        )
        cmds.showWindow(s.window)
        cmds.scriptJob(uid=[s.window, s.cleanup])

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
        if cmds.objExists(s.camera):
            cmds.delete(s.camera)

    def capture(s): # Ask for captures
        if s.callback(s.camera):
            cmds.deleteUI(s.window)
