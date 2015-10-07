# Working on things
import time
import os.path
import maya.cmds as cmds
from pprint import pprint
# Get all selected objects
objs = cmds.ls(sl=True, type="transform")

i18n = {
    "thumbNew" : {
        "title" : "Create Thumbnail"
        }
}

class ThumbNew(object):
    def __init__(s, i18n):
         """
         Create a new thumbnail GUI
         """
         s.i18n = i18n
         s.camName = "TempCam_%s" % int(time.time())
         s.camera = None
         s.createCam() # Create a temporary camera
         winName = "ThumbNEW"
         if cmds.window(winName, ex=True):
             cmds.deleteUI(winName)
         window = cmds.window(winName, t=i18n["thumbNew"]["title"], rtf=True)
         cmds.columnLayout(adj=True)
         cmds.text(l="HERE I AM!!!!")
         cmds.showWindow(window)
         cmds.scriptJob(uid=[window, s.cleanup])

    def createCam(s):
        if not cmds.objExists(s.camName):
            s.camera = cmds.camera(n=s.camName)[0]
            cmds.viewSet(s.camera, p=True) # Move camera to perspective position
            cmds.setAttr("%s.focalLength" % s.camera, 500)
            cmds.setAttr("%s.horizontalFilmAperture" % s.camera, 5)
            cmds.setAttr("%s.verticalFilmAperture" % s.camera, 5)
            cmds.setAttr("%s.visibility" % s.camera, 0)

    def cleanup(s):
        if cmds.objExists(s.camera):
            cmds.delete(s.camera)



ThumbNew(i18n)


		# 	cmds.viewSet(self.poseManCamera[0], p=1)
		# 	cmds.setAttr(self.poseManCamera[0] + ".focalLength", 100)
		# 	cmds.setAttr(self.poseManCamera[0] + ".visibility", 0)
		# """
		# # borramos todas las cameras de poseman
		# if len(self.camList) > 0:
		# 	cmds.delete(self.camList)
		# 	self.camList = []
        #
		# self.poseManCamera = cmds.camera(n="PoseManCaptureCam")
		# self.camList.append(self.poseManCamera[0])
		# cmds.viewSet(self.poseManCamera[0], p=1)
		# cmds.setAttr(self.poseManCamera[0] + ".focalLength", 100)
		# cmds.setAttr(self.poseManCamera[0] + ".visibility", 0)
        #
		# # delete window if exists
		# if cmds.window("capturePoseWindow", exists=1):
		# 	cmds.deleteUI("capturePoseWindow", window=1)
        #
		# # main window
		# self.poseManUI["capturePose"] = cmds.window("capturePoseWindow")
        #
		# # FrameLayout
		# FL = cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		# # RowColumnLayout with 6 rows
		# # 1 = capture viewport
		# # 2 = camera pre-set buttons
		# # 3 = section selection
		# # 4 = subsection selection
		# # 5 = enter pose name
		# # 6 = create, apply and cancel button
		# RL = cmds.rowColumnLayout(p=FL, nr=6, w=300)
        #
		# # 1
		# cmds.paneLayout("myPane", p=RL, w=300, h=350)
		# self.capturePoseModelPanel=cmds.modelPanel(mbv=0, camera=self.poseManCamera[0])
		# cmds.modelEditor(self.capturePoseModelPanel, e=1, grid=0, da="smoothShaded")
		# cmds.modelEditor(self.capturePoseModelPanel, e=1, allObjects=0)
		# cmds.modelEditor(self.capturePoseModelPanel, e=1, nurbsSurfaces=1)
		# cmds.modelEditor(self.capturePoseModelPanel, e=1, polymeshes=1)
		# cmds.modelEditor(self.capturePoseModelPanel, e=1, subdivSurfaces=1)
        #
		# # 2
		# cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		# cmds.rowColumnLayout(nc=5)
		# cmds.button(l="CamSet 1", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		# cmds.button(l="CamSet 2", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		# cmds.button(l="CamSet 3", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		# cmds.button(l="CamSet 4", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		# cmds.button(l="CamSet 5", bgc=(0.43, 0.63, 0.43), w=10,h=20)
        #
		# # 3
		# cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		# cmds.rowColumnLayout(nr=2)
		# cmds.text(align="left", label="Section")
		# self.poseManUI["optionSection"] = cmds.optionMenu(cc=partial(self.refreshSectionAndSubsectionOptionMenu))
        #
		# for section in self.getSections():
		# 	cmds.menuItem(label=section)
        #
		# # 4
		# cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		# cmds.rowColumnLayout(nr=2)
		# cmds.text(align="left", label="Sub Section")
		# self.poseManUI["optionSubSection"] = cmds.optionMenu()
		# currentSectionSelected = cmds.optionMenu(self.poseManUI["optionSection"], q=1, v=1)
        #
		# for section in self.getSubSections(currentSectionSelected):
		# 	cmds.menuItem(label=section)
        #
		# # 5
		# cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		# cmds.rowColumnLayout(nr=3)
		# cmds.text(align="left", label="Enter pose name:")
		# self.poseManUI["poseNameTextField"] = cmds.textField()
        #
		# # 6
		# cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		# cmds.rowColumnLayout(nc=3)
		# cmds.button(label="Create", c=partial(self.createNewPose, 1))
		# cmds.button(label="Apply", c=partial(self.createNewPose, 0))
		# cmds.button(label="Cancel", c=partial(self.deleteMyUI, "capturePoseWindow"))
        #
		# # show up window!
		# cmds.window("capturePoseWindow", e=1, rtf=0, t="New Pose", w=345, h=490)
		# cmds.showWindow("capturePoseWindow")
        #
		# # re-selection pose object list
		# if len(objList) > 0:
		# 	cmds.select(objList)
        #
		# # focus capture viewport and textField
		# cmds.setFocus(self.capturePoseModelPanel)
		# cmds.setFocus(self.poseManUI["poseNameTextField"])
        #
		# # select the actual section and the first sub-section
		# currentSelectedTab = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, sti=1)
		# cmds.optionMenu(self.poseManUI["optionSection"], e=1, sl=currentSelectedTab)
		# self.refreshSectionAndSubsectionOptionMenu()
