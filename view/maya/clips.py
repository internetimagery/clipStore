# Clips window

import maya.cmds as cmds

i18n = {
    "clips" : {
        "title"         : "Clips Menu",
        "editChar"      : "Click to change the characters details",
        "addClip"       : "Click to add clip to the scene",
        "editClip"      : "Change the clips details",
        "deleteClip"    : "Delete the clip.",
        "ignoreSel"     : "Apply the clip, ignoring anything selected.",
        "includeSel"    : "Apply the clip only to things selected.",
        "moreInfo"      : "Right click any Clip for more info and options. Drag the slider to resize clips."
    }
}

# Only pose selection
# Ignore selection
# Pose all

class Clips(object):
    def __init__(s, i18n, char, requestCharEdit, requestClipEdit, sendClip, sendDelClip):
        s.i18n = i18n
        s.char = char
        s.requestClipEdit = requestClipEdit # We're asking to edit the clip
        s.sendDelClip = sendDelClip
        s.sendClip = sendClip # User wants to place the clip
        name = "clipname"

        s.winName = "%sWin" % name
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t=s.i18n["title"])
        cmds.columnLayout(adj=True)
        cmds.rowLayout(nc=2, adj=2) # Open Row
        cmds.iconTextButton(
            ann=i18n["editChar"],
            style="iconOnly",
            font="boldLabelFont",
            image="smoothSkin.png",
            h=50,
            w=50,
            bgc=[0.3,0.3,0.3],
            c=requestCharEdit
        )
        cmds.text(
            l="<h1>%s</h1>" % name,
            hl=True,
            h=50
            )
        cmds.setParent("..") # Close row
        cmds.rowLayout(nc=2, adj=2) # Open Row
        cmds.columnLayout(adj=True) # Open Col
        s.includeSel = cmds.iconTextCheckBox(
            ann=i18n["includeSel"],
            style="iconOnly",
            font="boldLabelFont",
            image="channelBoxSlow.png",
            h=25,
            w=50,
            bgc=[0.3,0.3,0.3],
            cc=s.setInclude
        )
        s.ignoreSel = cmds.iconTextCheckBox(
            ann=i18n["ignoreSel"],
            style="iconOnly",
            font="boldLabelFont",
            image="channelBoxMedium.png",
            h=25,
            w=50,
            bgc=[0.3,0.3,0.3],
            cc=s.setIgnore
        )
        cmds.setParent("..") # Close Col
        cmds.button(
            l="CREATE NEW",
            h=50
            )
        cmds.setParent("..") # Close row
        cmds.separator()
        cmds.floatSlider(
            min=50,
            max=200,
            v=100,
            dc=s.sizeClips,
            h=20
            )
        cmds.frameLayout(l=i18n["moreInfo"], font="tinyBoldLabelFont")
        cmds.scrollLayout(cr=True, bgc=[0.2,0.2,0.2], h=400)
        s.wrapper = cmds.gridLayout(cwh=[100, 120], cr=True)
        cmds.showWindow(s.window)
        s.refresh()
    def setInclude(s, val):
        cmds.iconTextCheckBox(
            s.includeSel,
            e=True,
            bgc=[0.5,0.5,0.5] if val else [0.3,0.3,0.3],
            v=val
            )
        if val: s.setIgnore(False)
    def setIgnore(s, val):
        cmds.iconTextCheckBox(
            s.ignoreSel,
            e=True,
            bgc=[0.5,0.5,0.5] if val else [0.3,0.3,0.3],
            v=val
            )
        if val: s.setInclude(False)
    def sizeClips(s, val):
        cmds.gridLayout(s.wrapper, e=True, cwh=[val,val+20])
        if s.clips:
            for c in s.clips:
                c.resize(val)
    def refresh(s):
        try:
            cmds.deleteUI(cmds.layout(s.wrapper, q=True, ca=True))
        except RuntimeError:
            pass
        s.clips = []
        for c in range(20): # TODO, get these from the character
            s.clips.append(Clip(
                s.i18n,
                s.wrapper,
                c,
                s.sendClip,
                s.requestClipEdit,
                s.sendDelClip
                "ghostOff.png",
                "time.svg"
                ))
            s.clips[-1].resize(100)

class Clip(object):
    """
    Single clip
    """
    def __init__(s, i18n, parent, clip, sendClip, requestClipEdit, sendDelClip, imgSmall, imgLarge):
        cmds.columnLayout(adj=True, bgc=[0.1,0.1,0.1], p=parent)
        s.imgSmall = imgSmall
        s.imgLarge = imgLarge
        cmds.text(l="NAME OF CLIP", h=20)
        s.img = cmds.iconTextButton(
            l="",
            ann=i18n["addClip"],
            style="iconOnly",#"iconAndTextVertical",
            image=s.imgSmall,
            c=lambda: sendClip(clip)
            )
        cmds.popupMenu()
        cmds.menuItem(l=i18n["ignoreSel"])
        cmds.menuItem(ob=True, obi="channelBoxMedium.png")
        cmds.menuItem(l=i18n["includeSel"])
        cmds.menuItem(ob=True, obi="channelBoxSlow.png")
        cmds.menuItem(d=True)
        cmds.menuItem(l=i18n["editClip"])
        cmds.menuItem(ob=True, obi="pencilCursor.png")
        cmds.menuItem(l=i18n["deleteClip"], c=lambda: sendDelClip(clip))
        cmds.menuItem(ob=True, obi="SP_TrashIcon.png")
    def resize(s, size):
        img = s.imgSmall if size < 150 else s.imgLarge
        cmds.iconTextButton(s.img, e=True, w=size, h=size, i=img)

#
def test(*args):
    print "edit", args

Clips(i18n["clips"], None, test, test, test, test)
