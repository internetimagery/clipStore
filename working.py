# Working on things
import os.path
import maya.cmds as cmds
from pprint import pprint
# Get all selected objects
objs = cmds.ls(sl=True, type="transform")
