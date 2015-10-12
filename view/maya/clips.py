# Clips window

import maya.cmds as cmds
import warn

class Clips(object):
    def __init__(s, i18n, char, requestCharEdit, requestClipEdit, sendClip, sendDelClip):
        s.i18n = i18n
        s.char = char
        s.requestClipEdit = requestClipEdit # We're asking to edit the clip
        s.sendDelClip = sendDelClip
        s.sendClip = sendClip # User wants to place the clip
        s.clips = [] # Init clips!
        name = s.char.metadata["name"].title()

        s.winName = "%sWin" % name
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t="%s %s" % (name, i18n["title"]))
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
            c=lambda: warn.run(requestCharEdit, s.char)
        )
        cmds.text(
            l="<h1>%s</h1>" % name,
            hl=True,
            h=50
            )
        cmds.setParent("..") # Close row
        cmds.columnLayout(adj=True) # Open Col
        cmds.button(
            l=i18n["newClip"],
            h=50
            )
        cmds.setParent("..") # Close row
        cmds.floatSlider(
            min=50,
            max=200,
            v=100,
            dc=s.sizeClips,
            h=20
            )
        cmds.separator()
        cmds.frameLayout(l=i18n["moreInfo"], font="tinyBoldLabelFont")
        cmds.scrollLayout(cr=True, mcw=400, bgc=[0.2,0.2,0.2], h=400)
        s.wrapper = cmds.gridLayout(cwh=[100, 120], cr=True)
        cmds.setParent("..") # Close grid
        cmds.setParent("..") # Close Scroll
        cmds.separator()
        cmds.showWindow(s.window)
        cmds.scriptJob(uid=[s.window, s.cleanup], ro=True)
        s.refresh()
    def cleanup(s):
        print "cleanup"
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
                s.sendDelClip,
                "ghostOff.png",
                "time.svg"
                ))
            s.clips[-1].resize(100)

class Clip(object):
    """
    Single clip
    """
    def __init__(s, i18n, parent, clip, sendClip, requestClipEdit, sendDelClip, imgSmall, imgLarge):
        cmds.columnLayout(adj=True, bgc=[0.18,0.18,0.18], p=parent)
        s.imgSmall = imgSmall
        s.imgLarge = imgLarge
        s.img = cmds.iconTextButton(
            l="",
            ann=i18n["addClip"],
            style="iconOnly",#"iconAndTextVertical",
            image=s.imgSmall,
            c=lambda: sendClip(clip)
            )
        cmds.text(l="CLIPNAME", h=20)
        cmds.popupMenu(p=s.img)
        cmds.menuItem(l="CLIPNAME", en=False, itl=True)
        cmds.menuItem(l=i18n["ignoreSel"])
        cmds.menuItem(ob=True, obi="channelBoxMedium.png")
        cmds.menuItem(l=i18n["includeSel"])
        cmds.menuItem(ob=True, obi="channelBoxSlow.png")
        cmds.menuItem(d=True)
        cmds.menuItem(l=i18n["editClip"], c=lambda x: requestClipEdit(clip))
        cmds.menuItem(ob=True, obi="pencilCursor.png")
        cmds.menuItem(l=i18n["deleteClip"], c=lambda x: sendDelClip(clip))
        cmds.menuItem(ob=True, obi="SP_TrashIcon.png")
    def resize(s, size):
        img = s.imgSmall if size < 150 else s.imgLarge
        cmds.iconTextButton(s.img, e=True, w=size, h=size, i=img)
