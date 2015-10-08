# Save Characters as files. Clips within the file


import maya.cmds as cmds

i18n = {
    "characterNew"  : {
        "title"     : "Modify Character",
        "obj"       : "Add selected objects",
        "objDesc"   : "Click to add selected objects",
        "objbtnDesc": "Click to select object. Double click to rename.",
        "filter"    : "Include Attributes",
    }
}

class CharacterNew(object):
    """
    Create a new character gui
    """
    def __init__(s, i18n, overrides=None):
        s.i18n = i18n
        s.data = overrides.copy() if overrides else {}
        winName = "CharacterNewWin"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.window = cmds.window(t=s.i18n["title"], rtf=True)
        cmds.columnLayout(adj=True)
        row1 = 150 #rwo width
        col1 = [0.22,0.22,0.22]
        col2 = [0.25,0.25,0.25]
        # ADD OBJECTS
        cmds.rowLayout(nc=2, adj=2, bgc=col1)
        cmds.text(h=30, w=row1, l=s.i18n["obj"])
        cmds.columnLayout(adj=True)
        cmds.iconTextButton(
            l=s.i18n["objDesc"],
            image="selectByObject.png",
            style="iconAndTextHorizontal",
            h=30,
            c=s.addObjects
        )
        s.objwrapper = cmds.scrollLayout(cr=True, bgc=[0.2,0.2,0.2])
        cmds.setParent("..") # close scroll
        cmds.setParent("..") # Close column
        cmds.setParent("..") # Close row
        # FILTER ATTRIBUTES
        cmds.rowLayout(nc=2, adj=2, bgc=col1)
        cmds.text(h=30, w=row1, l=s.i18n["filter"])
        s.attrwrapper = cmds.scrollLayout(cr=True, bgc=[0.2,0.2,0.2])
        cmds.setParent("..") # close scroll
        cmds.setParent("..") # Close row
        cmds.showWindow(s.window)
    def clearLayout(s, layout):
        children = cmds.layout(layout, q=True, ca=True)
        if children:
            for c in children:
                try: cmds.deleteUI(c)
                except RuntimeError: pass
    def addObjects(s):
        s.data["objs"] = s.data.get("objs", set())
        s.data["objs"] |= set(cmds.ls(sl=True, type="transform"))
        attrs = set(cmds.listAttr(list(s.data["objs"]), k=True)) if s.data["objs"] else set()
        s.displayObjects()
        # s.displayFilters(attrs)
    def displayObjects(s):
        s.clearLayout(s.objwrapper)
        if s.data.get("objs", None):
            def addObj(obj):
                def remObj():
                    s.data["objs"].remove(obj)
                    cmds.layout(row, e=True, m=False)
                def selectObj(): cmds.select(obj, r=True)
                def renameObj(text):
                    cmds.iconTextButton(btn, e=True, m=True, l=text)
                    cmds.textField(editText, e=True, m=False)
                    print "rename!", text
                def enableEdit():
                    cmds.control(btn, e=True, m=False)
                    cmds.control(editText, e=True, m=True)
                row = cmds.rowLayout(nc=2, adj=1, p=s.objwrapper)
                col = cmds.columnLayout(adj=True)
                btn = cmds.iconTextButton(
                    l=obj,
                    image="cube.png",
                    style="iconAndTextHorizontal",
                    h=35,
                    c=selectObj,
                    dcc=lambda: enableEdit()
                )
                editText = cmds.textField(
                    tx=obj,
                    aie=True,
                    h=35,
                    ec=lambda x: renameObj(x),
                    m=False
                )
                cmds.setParent("..")
                cmds.iconTextButton(
                    image="removeRenderable.png",
                    style="iconOnly",
                    h=35,
                    w=35,
                    c=remObj
                )
                cmds.setParent("..")
                pass
            for obj in s.data["objs"]:
                addObj(obj)

    def buildObjs(s, obj):
        pass
    def displayFilters(s, attrs):
        s.clearLayout(s.whitelist)
        s.clearLayout(s.blacklist)
        def addFilter(parent, listing, name):
            exist = s.data.get(listing, [])
            btn = cmds.iconTextCheckBox(
                l=name,
                image="currentNamespace.png" if name in exist else "closeAttribute.png",
                v=True if name in exist else False
            )
        if attrs:
            for at in attr:
                addFilter(s.whitelist, "whitelist", at)
                addFilter(s.blacklist, "blacklist", at)

CharacterNew(i18n["characterNew"])
