# Clips window

import maya.utils as utils
import maya.cmds as cmds
import threading
import time
import warn

class Clips(object):
    def __init__(s, i18n, char, requestCharEdit, requestClipEdit, requestClipThumbs, sendRunClip):
        s.i18n = i18n
        s.char = char
        s.requestClipEdit = requestClipEdit # We're asking to edit the clip
        s.requestClipThumbs = requestClipThumbs # Grab thumbnails
        s.sendRunClip = sendRunClip # User wants to place the clip
        s.clips = [] # Init clips!
        name = s.char.metadata["name"].title()

        if not char.data: # Does the character contain nothing?
            with warn:
                requestCharEdit(char, s.refresh)

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
            c=lambda: requestCharEdit(s.char, s.refresh)
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
            c=lambda x: warn.run(requestClipEdit, s.char, s.refresh)
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
    def refresh(s, *nothing):
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
                    s.requestClipThumbs,
                    s.sendRunClip,
                    s.refresh
                    ))
                s.clips[-1].resize(100)
            AnimManager(s.wrapper, s.clips).play()

class Clip(object):
    """
    Single clip
    """
    def __init__(s, i18n, parent, char, clip, requestClipThumbs, sendRunClip, refresh):
        cmds.columnLayout(adj=True, bgc=[0.18,0.18,0.18], p=parent) # Main block
        s.i18n = i18n
        s.name = clip.metadata["name"].title()
        s.thumbs = requestClipThumbs(char, clip)
        if s.thumbs:
            s.thumbs.reverse()
        else:
            s.thumbs = ["ghostOff.png"]
        s.index = 0
        s.imgbtn = cmds.iconTextButton(
            ann=i18n["clips.addClip"],
            style="iconOnly",#"iconAndTextVertical",
            image=s.thumbs[0],
            c=lambda: warn.run(sendRunClip, char, clip)
            )
        s.label = cmds.text(l=s.name, h=20)
        cmds.popupMenu(p=s.imgbtn)
        cmds.menuItem(l=s.name, en=False, itl=True)
        cmds.menuItem(l=i18n["clips.ignoreSel"], c=lambda x: warn.run(sendRunClip, char, clip, ignore=True))
        cmds.menuItem(ob=True, obi="channelBoxMedium.png")
        cmds.menuItem(l=i18n["clips.includeSel"], c=lambda x: warn.run(sendRunClip, char, clip, include=True))
        cmds.menuItem(ob=True, obi="channelBoxSlow.png")
        cmds.menuItem(d=True)
        cmds.menuItem(l=i18n["clips.renameClip"], c=lambda x: s.rename(char, clip))
        cmds.menuItem(ob=True, obi="pencilCursor.png")
        cmds.menuItem(l=i18n["clips.deleteClip"], c=lambda x: refresh(warn.run(char.removeClip, clip)))
        cmds.menuItem(ob=True, obi="SP_TrashIcon.png")
    def resize(s, size):
        # img = s.imgSmall if size < 150 else s.imgLarge
        # cmds.iconTextButton(s.img, e=True, w=size, h=size, i=img)
        cmds.iconTextButton(s.imgbtn, e=True, w=size, h=size)
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
    def next(s):
        s.index = s.index - 1 if s.index else len(s.thumbs) - 1
        cmds.iconTextButton(s.imgbtn, e=True, image=s.thumbs[s.index])

# import traceback, sys

class AnimManager(object):
    """
    Play animations on the buttons.
    """
    def __init__(s, wrapper, anims):
        s.wrapper = wrapper
        s.anims = anims
        s.stop = False
    def tick(s):
        try:
            if not cmds.layout(s.wrapper, ex=True): raise RuntimeError
            for anim in s.anims:
                anim.next() # Next frame
        except:
            # traceback.print_exception(*sys.exc_info())
            print "Animation Stopped."
            s.stop = True
    def run(s):
        while not s.stop:
            utils.executeDeferred(s.tick)
            time.sleep(1)
    def play(s):
        threading.Thread(target=s.run).start()
