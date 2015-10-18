# Pick a folder and display all character files within
# Created 10/10/15 Jason Dixon
# http://internetimagery.com

import maya.cmds as cmds
import fileDialog
import os.path
import warn
import os

class Selector(object):
    def __init__(s, i18n, requestExtension, sendNew, sendOpen):
        s.i18n = i18n
        s.ext = requestExtension
        s.sendNew = sendNew
        s.sendOpen = sendOpen # Ask to open a file
        path = cmds.workspace(q=True, rd=True) # Default starting Dir
        if "default" in path: # Ignore default workspace...
            path = os.path.expanduser("~")
        s.files = {}

        s.winName = "SelectorWin"
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
            c=s.loadExisting
        )
        cmds.iconTextButton(
            l=i18n["selector.new"],
            style="iconAndTextHorizontal",
            font="boldLabelFont",
            image="publishAttributes.png",#"Ghost_ON.png",
            h=30,
            c=s.createNew
        )
        cmds.separator()
        s.wrapper = cmds.columnLayout(adj=True)
        cmds.columnLayout() # Here for deletion
        cmds.showWindow(s.window)
        s.openFolder(path)

    def createNew(s):
        path = fileDialog.FileDialog(s.i18n).save(s.ext)
        if path:
            s.sendNew(path)
            s.openFolder(os.path.dirname(path))

    def loadExisting(s):
        path = fileDialog.FileDialog(s.i18n).load(s.ext)
        if path:
            s.sendOpen(path)
            s.openFolder(os.path.dirname(path))

    def openFolder(s, root):
        cmds.deleteUI(cmds.layout(s.wrapper, q=True, ca=True))
        cmds.columnLayout(adj=True, p=s.wrapper)
        def addItem(name, path, folder=False):
            cmds.iconTextButton(
                l=name.title(),
                style="iconAndTextHorizontal",
                font="boldLabelFont",
                image="SP_DirClosedIcon.png" if folder else "polyColorSetEditor.png",
                h=40,
                bgc=[0.22,0.22,0.22] if folder else [0.2,0.2,0.2],
                c=lambda: warn.run(s.openFolder if folder else s.sendOpen, path)
            )
        def addShortcut(index):
            if rootParts[index]:
                cmds.button(
                    l=rootParts[index],
                    c=lambda x: s.openFolder(os.sep.join(rootParts[:index + 1]))
                )
        root = os.path.realpath(root)
        cmds.rowLayout(nc=100)
        rootParts = root.split(os.sep)
        for i in range(len(rootParts)):
            addShortcut(i)
        cmds.setParent("..")
        cmds.scrollLayout(cr=True, h=400, bgc=[0.2,0.2,0.2])
        files = os.listdir(root)
        if files:
            for f in files:
                path = os.path.join(root, f)
                if os.path.isdir(path) and f[:1] != ".":
                    addItem(f, path, True)
                elif os.path.isfile(path) and f.endswith(s.ext):
                    addItem(f, path)
        else:
            cmds.text(l=s.i18n["selector.none"])
