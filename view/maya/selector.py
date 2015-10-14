# Pick a folder and display all character files within
# Created 10/10/15 Jason Dixon
# http://internetimagery.com

import maya.cmds as cmds
import os.path
import os

class Selector(object):
    def __init__(s, i18n, requestFiles, requestNew, sendOpen):
        s.i18n = i18n
        s.sendOpen = sendOpen # Ask to open a file
        path = cmds.workspace(q=True, rd=True) # Default starting Dir
        s.files = {}

        s.winName = "PrimaryWin"
        if cmds.window(s.winName, ex=True):
            cmds.deleteUI(s.winName)
        s.window = cmds.window(s.winName, rtf=True, t=s.i18n["selector.title"])
        cmds.columnLayout(adj=True)
        cmds.iconTextButton(
            l=i18n["selector.open"],
            style="iconAndTextHorizontal",
            font="boldLabelFont",
            image="SP_DirOpenIcon.png",
            h=30,
            c=lambda: s.addFiles(requestFiles())
        )
        cmds.iconTextButton(
            l=i18n["selector.new"],
            style="iconAndTextHorizontal",
            font="boldLabelFont",
            image="publishAttributes.png",#"Ghost_ON.png",
            h=30,
            c=requestNew
        )
        cmds.separator()
        cmds.scrollLayout(cr=True, h=400, bgc=[0.2,0.2,0.2])
        s.wrapper = cmds.columnLayout(adj=True)
        cmds.columnLayout()
        cmds.showWindow(s.window)
        s.addFiles(requestFiles(path))

    def addFiles(s, files):
        cmds.deleteUI(cmds.layout(s.wrapper, q=True, ca=True))
        cmds.columnLayout(adj=True, p=s.wrapper)
        def addChar(f):
            def load():
                s.sendOpen(f)
            cmds.iconTextButton(
                l=os.path.basename(os.path.splitext(f)[0]).title(),
                style="iconAndTextHorizontal",
                font="boldLabelFont",
                image="polyColorSetEditor.png",
                h=40,
                c=load
            )
        if files:
            for f in files:
                addChar(f)
        else:
            cmds.text(l=s.i18n["selector.none"])
