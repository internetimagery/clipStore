

# animated images in button
import maya.cmds as cmds
import maya.utils as utils
import time
from threading import Thread

win = cmds.window()
cmds.columnLayout()
btn = cmds.iconTextButton(
            style="iconOnly",
            image="goToBindPose.png",
            h=50,
            w=50,
        )
cmds.showWindow(win)

class Anim(object):
    def __init__(s, element, images):
        s.element = element
        s.images = images
        s.index = 0
    def next(s):
        s.index = s.index - 1 if s.index else len(s.images) - 1
        cmds.iconTextButton(s.btn, e=True, image=s.images[s.index])

class AnimManager(object):
    def __init__(s, anims):
        s.anims = anims
    def update(s):
        anims = []
        for anim in s.anims:
            if anim.next():
                anims.append(anim)
        s.anims = anims
    def run(s):
        while True:
            if s.anims:
                utils.executeDeferred(s.update)
                time.sleep(1)
            else:
                break

images = ["activeDeselectedAnimLayer.png", "activeSelectedAnimLayer.png"]

def switch():
    buttons = [t(btn, images)]
    while True:
        if not buttons:
            break
        time.sleep(1)
        for b in buttons:
            if not utils.executeInMainThreadWithResult(b.run):
                buttons.remove(b)

Thread(target=switch).start()
