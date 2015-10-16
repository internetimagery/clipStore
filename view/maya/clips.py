# Clips window

import maya.utils as utils
import maya.cmds as cmds
import traceback
import threading
import time
import warn
import sys

class Clips(object):
    def __init__(s, i18n, char, requestCharEdit, requestClipEdit, sendRunClip):
        s.i18n = i18n
        s.char = char
        s.requestClipEdit = requestClipEdit # We're asking to edit the clip
        s.sendRunClip = sendRunClip # User wants to place the clip
        s.clips = [] # Init clips!
        name = s.char.metadata["name"].title()

        if not char.data: # Does the character contain nothing?
            with warn:
                requestCharEdit(char, s.refresh)

        s.winName = "%sWin" % name
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, s=False, t="%s %s" % (name, i18n["clips.title"]))
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
        cmds.scrollLayout(cr=True, bgc=[0.2,0.2,0.2], h=400)
        s.wrapper = cmds.gridLayout(w=400, cwh=[100, 120], cr=True, aec=False)
        cmds.setParent("..") # Close grid
        cmds.setParent("..") # Close Scroll
        cmds.separator()
        cmds.showWindow(s.window)
        cmds.scriptJob(uid=[s.window, s.cleanup], ro=True)
        s.refresh()
    def cleanup(s):
        print "Closed"
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
        try:
            s.clips = [] # GUI clips
            if s.char.clips:
                for c in sorted(s.char.clips, key=lambda x: x.metadata.get("name", "zzzz")):
                    s.clips.append(Clip(
                        s.i18n,
                        s.wrapper,
                        s.char,
                        c,
                        s.sendRunClip,
                        s.refresh
                        ))
                    s.clips[-1].resize(100)
                AnimManager(s.wrapper, s.clips).play()
        except:
            traceback.print_exception(*sys.exc_info())

class Clip(object):
    """
    Single clip
    """
    def __init__(s, i18n, parent, char, clip, sendRunClip, refresh):
        s.wrapper = cmds.columnLayout(adj=True, bgc=[0.18,0.18,0.18], p=parent) # Main block
        s.i18n = i18n
        s.char = char
        s.clip = clip
        s.name = clip.metadata["name"].title()
        length = clip.metadata.get("length", None)
        if length is not None:
            s.name = "%s - %s" % (s.name, length)
        s.thumbs = list(clip.thumbs) if clip.thumbs else ["savePaintSnapshot.png"]
        s.thumbs.reverse()
        s.index = 0
        s.imgbtn = cmds.iconTextButton(
            ann=i18n["clips.addClip"],
            style="iconOnly",#"iconAndTextVertical",
            image=s.thumbs[-1],
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
        cmds.menuItem(l=i18n["clips.deleteClip"], c=lambda x: s.delete())
        cmds.menuItem(ob=True, obi="SP_TrashIcon.png")
    def delete(s):
        # Delete itself
        with warn:
            ans = cmds.confirmDialog(
                t=s.i18n["clips.deleteClip"],
                m=s.i18n["clips.deleteConfirm"],
                button=[s.i18n["yes"], s.i18n["no"]],
                defaultButton=s.i18n["yes"],
                cancelButton=s.i18n["no"],
                dismissString=s.i18n["no"]
                )
            if ans == s.i18n["yes"]: # Are we ok to delete??
                s.char.removeClip(s.clip)
                cmds.layout(s.wrapper, e=True, m=False)
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
        s.index = s.index - 1 if 0 <= s.index else len(s.thumbs) - 1
        cmds.iconTextButton(s.imgbtn, e=True, image=s.thumbs[s.index])

class AnimManager(object):
    def __init__(s, wrapper, anims):
        s.wrapper = wrapper
        s.anims = anims
        s.img = cmds.iconTextStaticLabel(style="iconOnly")
        s.playing = False
        s.limit = threading.Semaphore(1) # Limit calls while maya is busy
    def tick(s):
        try:
            if not cmds.layout(s.wrapper, ex=True): raise RuntimeError
            for anim in s.anims:
                anim.next() # Next frame
        except:
            # traceback.print_exception(*sys.exc_info())
            s.playing = False
        finally:
            s.limit.release()
    def play(s):
        if not s.playing:
            def go():
                while s.playing:
                    s.limit.acquire()
                    utils.executeDeferred(s.tick)
                    time.sleep(1)
            s.playing = True
            threading.Thread(target=go).start()
    def stop(s):
        s.playing = False
