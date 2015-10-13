# Clips window

import maya.cmds as cmds
import warn

class Clips(object):
    def __init__(s, i18n, char, requestCharEdit, requestClipEdit, sendRunClip, sendDelClip):
        s.i18n = i18n
        s.char = char
        s.requestClipEdit = requestClipEdit # We're asking to edit the clip
        s.sendDelClip = sendDelClip
        s.sendRunClip = sendRunClip # User wants to place the clip
        s.clips = [] # Init clips!
        name = s.char.metadata["name"].title()

        s.winName = "%sWin" % name
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t="%s %s" % (name, i18n["clips.title"]))
        cmds.columnLayout(adj=True)
        cmds.rowLayout(nc=2, adj=2) # Open Row
        cmds.iconTextButton(
            ann=i18n["clips.editChar"],
            style="iconOnly",
            font="boldLabelFont",
            image="goToBindPose.png",
            h=50,
            w=50,
            bgc=[0.3,0.3,0.3],
            c=lambda: requestCharEdit(s.char)
        )
        cmds.text(
            l="<h1>%s</h1>" % name,
            hl=True,
            h=50
            )
        cmds.setParent("..") # Close row
        cmds.columnLayout(adj=True) # Open Col
        cmds.button(
            l=i18n["clips.newClip"],
            h=50,
            c=lambda x: warn.run(requestClipEdit, s.char)
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
        cmds.frameLayout(l=i18n["clips.moreInfo"], font="tinyBoldLabelFont")
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
        s.clips = [] # GUI clips
        if s.char.clips:
            for c in s.char.clips:
                s.clips.append(Clip(
                    s.i18n,
                    s.wrapper,
                    s.char,
                    c,
                    s.sendRunClip,
                    s.requestClipEdit,
                    s.sendDelClip,
                    ))
                s.clips[-1].resize(100)

class Clip(object):
    """
    Single clip
    """
    def __init__(s, i18n, parent, char, clip, sendRunClip, requestClipEdit, sendDelClip):
        cmds.columnLayout(adj=True, bgc=[0.18,0.18,0.18], p=parent) # Main block
        s.name = clip.metadata["name"].title()
        # s.imgSmall = char.cache(clip.metadata["thumbs"]["small"]) if clip.metadata["thumbs"].get("small", False) else "ghostOff.png"
        s.imgLarge = char.cache(clip.metadata["thumbs"]["large"]) if clip.metadata["thumbs"].get("large", False) else "ghostOff.png"
        s.img = cmds.iconTextButton(
            l="",
            ann=i18n["clips.addClip"],
            style="iconOnly",#"iconAndTextVertical",
            image=s.imgLarge,
            c=lambda: warn.run(sendRunClip, clip)
            )
        cmds.text(l=s.name, h=20)
        cmds.popupMenu(p=s.img)
        cmds.menuItem(l=s.name, en=False, itl=True)
        cmds.menuItem(l=i18n["clips.ignoreSel"])
        cmds.menuItem(ob=True, obi="channelBoxMedium.png")
        cmds.menuItem(l=i18n["clips.includeSel"])
        cmds.menuItem(ob=True, obi="channelBoxSlow.png")
        cmds.menuItem(d=True)
        cmds.menuItem(l=i18n["clips.renameClip"], c=lambda x: rename(clip))
        cmds.menuItem(ob=True, obi="pencilCursor.png")
        cmds.menuItem(l=i18n["clips.deleteClip"], c=lambda x: sendDelClip(char, clip))
        cmds.menuItem(ob=True, obi="SP_TrashIcon.png")
    def resize(s, size):
        # img = s.imgSmall if size < 150 else s.imgLarge
        # cmds.iconTextButton(s.img, e=True, w=size, h=size, i=img)
        cmds.iconTextButton(s.img, e=True, w=size, h=size)
    def rename(s, clip):
        print "rename"
