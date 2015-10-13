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
            print "Cleaned tempfile:", s
    def __getattribute__(s, k):
        raise AttributeError, "\"Temp_Path\" cannot be modified with \"%s\"" % k

def CaptureThumb(pixels, camera):
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
    frame = cmds.currentTime(q=True) # Get current time
    imgFormat = cmds.getAttr("defaultRenderGlobals.imageFormat")
    selection = cmds.ls(sl=True)
    # Create a temporary file to hold the thumbnail
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f: path = Temp_Path(f.name)
    # Capture our thumbnail
    try:
        cmds.modelEditor(view, e=True, camera=camera) # Change to camera
        cmds.modelEditor(view, e=True, displayAppearance="smoothShaded") # Set display mode
        cmds.select(cl=True) # Clear selection for pretty image
        cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
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
        cmds.setAttr("defaultRenderGlobals.imageFormat", imgFormat)
        cmds.select(selection, r=True)
        cmds.modelEditor(view, e=True, camera=oldCam)
        cmds.modelEditor(view, e=True, displayAppearance=display)
    return path
