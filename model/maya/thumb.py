# Capture a thumbnail image into a temporary file
# Created 13/10/15 Jason Dixon
# http://internetimagery.com

import os
import os.path
import tempfile
import maya.cmds as cmds

class Temp_Path(str):
    def __del__(s):
        if os.path.isfile(s):
            os.remove(s)
            # print "Cleaned tempfile:", s
    def __getattribute__(s, k):
        if k[0] == "_": return str.__getattribute__(s, k)
        raise AttributeError, "\"Temp_Path\" cannot be modified with \"%s\"" % k

class Thumb(object):
    """
    Capture thumbnails etc
    """
    def capture(s, pixels, camera, frame):
        """
        Capture a thumbnail
        """
        # Validate our inputs
        if not cmds.objExists(camera):
            raise RuntimeError, "%s does not exist." % camera
        if not pixels or type(pixels) != int:
            raise RuntimeError, "No valid size provided"
        # Collect information:
        view = cmds.playblast(activeEditor=True) # Panel to capture from
        oldCam = cmds.modelEditor(view, q=True, camera=True) # Existing camera
        display = cmds.modelEditor(view, q=True, displayAppearance=True)
        oldFrame = cmds.currentTime(q=True) # Get current time
        imgFormat = cmds.getAttr("defaultRenderGlobals.imageFormat")
        selection = cmds.ls(sl=True) # Current selection
        playWin = cmds.playblast(ae=True) # Get playblast window
        playDa = cmds.modelEditor(playWin, q=True, da=True)
        playGrid = cmds.modelEditor(playWin, q=True, grid=True)
        playAllObjects = True if cmds.modelEditor(playWin, q=True, allObjects=True) else False
        playPolymeshes = cmds.modelEditor(playWin, q=True, polymeshes=True)
        playAurbsSurfaces = cmds.modelEditor(playWin, q=True, nurbsSurfaces=True)
        playSubdivSurfaces = cmds.modelEditor(playWin, q=True, subdivSurfaces=True)
        playDisplayTextures = cmds.modelEditor(playWin, q=True, displayTextures=True)
        # Create a temporary file to hold the thumbnail
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f: path = Temp_Path(f.name)
        # Capture our thumbnail
        try:
            cmds.currentTime(frame)
            cmds.modelEditor(view, e=True, camera=camera) # Change to camera
            cmds.modelEditor(view, e=True, displayAppearance="smoothShaded") # Set display mode
            cmds.select(cl=True) # Clear selection for pretty image
            cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
            cmds.modelEditor( # Tweak nice default visuals
                playWin,
                e=True,
                grid=False,
                da="smoothShaded",
                allObjects=False,
                nurbsSurfaces=True,
                polymeshes=True,
                subdivSurfaces=True,
                displayTextures=True
                )
            cmds.playblast(
                frame=frame, # Frame range
                fo=True, # Force override the file if it exists
                viewer=False, # Don't popup window during render
                width=pixels*2, # Width in pixels, duh
                height=pixels*2, # Height in pixels. Who knew
                showOrnaments=False, # Hide tools, ie move tool etc
                format="image", # We just want a single image
                completeFilename=f.name.replace("\\", "/") # Output file
                )
        # Put everything back as we found it.
        finally:
            cmds.currentTime(oldFrame)
            cmds.select(selection, r=True)
            cmds.modelEditor(view, e=True, camera=oldCam)
            cmds.modelEditor(view, e=True, displayAppearance=display)
            cmds.setAttr("defaultRenderGlobals.imageFormat", imgFormat)
            # Reset playblast options
            cmds.modelEditor( # Tweak nice default visuals
                playWin,
                e=True,
                grid=playGrid,
                da=playDa,
                allObjects=playAllObjects,
                nurbsSurfaces=playAurbsSurfaces,
                polymeshes=playPolymeshes,
                subdivSurfaces=playSubdivSurfaces,
                displayTextures=playDisplayTextures
                )
        return path

Thumb = Thumb()
