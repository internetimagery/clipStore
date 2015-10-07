
import os.path
import maya.cmds as cmds

def CaptureThumb(pixels, camera, path):
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
    # Capture our thumbnail
    try:
        cmds.modelEditor(view, e=True, camera=camera) # Change to camera
        cmds.modelEditor(view, e=True, displayAppearance="smoothShaded") # Set display mode
        cmds.select(cl=True) # Clear selection for pretty image
        cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
        cmds.playblast(
            frame=frame, # Frame range
            viewer=False, # Don't popup window during render
            width=pixels*2, # Width in pixels, duh
            height=pixels*2, # Height in pixels. Who knew
            showOrnaments=False, # Hide tools, ie move tool etc
            format="image", # We just want a single image
            completeFilename=path.replace("\\", "/") # Output file
            )
    # Put everything back as we found it.
    finally:
        cmds.setAttr("defaultRenderGlobals.imageFormat", imgFormat)
        cmds.select(selection, r=True)
        cmds.modelEditor(view, e=True, camera=oldCam)
        cmds.modelEditor(view, e=True, displayAppearance=display)
