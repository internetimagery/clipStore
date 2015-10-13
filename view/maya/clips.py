# Clips window

import maya.cmds as cmds
import warn

class Clips(object):
    def __init__(s, i18n, char, requestCharEdit, requestClipEdit, sendRunClip):
        s.i18n = i18n
        s.char = char
        s.requestClipEdit = requestClipEdit # We're asking to edit the clip
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
                    s.sendRunClip
                    ))
                s.clips[-1].resize(100)

class Clip(object):
    """
    Single clip
    """
    def __init__(s, i18n, parent, char, clip, sendRunClip):
        cmds.columnLayout(adj=True, bgc=[0.18,0.18,0.18], p=parent) # Main block
        s.i18n = i18n
        s.name = clip.metadata["name"].title()
        # s.imgSmall = char.cache(clip.metadata["thumbs"]["small"]) if clip.metadata["thumbs"].get("small", False) else "ghostOff.png"
        s.imgLarge = char.cache(clip.metadata["thumbs"]["large"]) if clip.metadata["thumbs"].get("large", False) else "ghostOff.png"
        s.img = cmds.iconTextButton(
            ann=i18n["clips.addClip"],
            style="iconOnly",#"iconAndTextVertical",
            image=s.imgLarge,
            c=lambda: warn.run(sendRunClip, char, clip)
            )
        s.label = cmds.text(l=s.name, h=20)
        cmds.popupMenu(p=s.img)
        cmds.menuItem(l=s.name, en=False, itl=True)
        cmds.menuItem(l=i18n["clips.ignoreSel"], c=lambda x: warn.run(sendRunClip, char, clip, ignore=True))
        cmds.menuItem(ob=True, obi="channelBoxMedium.png")
        cmds.menuItem(l=i18n["clips.includeSel"], c=lambda x: warn.run(sendRunClip, char, clip, include=True))
        cmds.menuItem(ob=True, obi="channelBoxSlow.png")
        cmds.menuItem(d=True)
        cmds.menuItem(l=i18n["clips.renameClip"], c=lambda x: s.rename(char, clip))
        cmds.menuItem(ob=True, obi="pencilCursor.png")
        cmds.menuItem(l=i18n["clips.deleteClip"], c=lambda x: warn.run(char.removeClip, clip))
        cmds.menuItem(ob=True, obi="SP_TrashIcon.png")
    def resize(s, size):
        # img = s.imgSmall if size < 150 else s.imgLarge
        # cmds.iconTextButton(s.img, e=True, w=size, h=size, i=img)
        cmds.iconTextButton(s.img, e=True, w=size, h=size)
    def rename(s, char, clip):
        result = cmds.promptDialog(
    		title=s.i18n["clips.renameClip"],
    		message=s.i18n["clips.enterName"],
    		button=[s.i18n["ok"], s.i18n["cancel"]],
    		defaultButton=s.i18n["ok"],
    		cancelButton=s.i18n["cancel"],
    		dismissString=s.i18n["cancel"])
        text = cmds.promptDialog(query=True, text=True)
        if result == s.i18n["ok"] and text:
            text = text.strip().title() if text else None
            if text:
                clip.metadata["name"] = text
                char.save()
                cmds.text(s.label, e=True, l=text)
