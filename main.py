# Lets run this thing!!
import character
import os.path
import os

class Main(object):
    def __init__(s, i18n, view, model, software):
        s.i18n = i18n
        s.view = view
        s.model = model
        s.software = software

        s.ext = ".char" # File extension!

        # Load our Selector window
        view.selector(
            s.i18n["selector"],
            s.sendFiles,
            s.characterNew,
            s.characterLoad
            )
    def sendFiles(s, path=None):
        """
        Given user input path, list character files
        """
        if not path:
            path = s.view.fileDialog(s.i18n["filedialog"]).openDir()
        if path:
            path = os.path.realpath(path)
            return [os.path.join(path, f) for f in os.listdir(path) if s.ext in f]
    def characterNew(s):
        """
        Create a new character!
        """
        path = s.view.fileDialog(s.i18n["filedialog"]).save()
        if path:
            if os.path.isfile(path): os.remove(path)
            s.characterLoad(path)
            # TODO add opening of character edit window here
    def characterLoad(s, path):
        """
        Open an existing character!
        """
        path = os.path.realpath(path)
        if os.path.isfile(path):
            c = character.Character(path, s.software)
            if c.metadata["software"] == s.software:
                s.view.clips(
                    s.i18n["clips"],
                    c,
                    s.characterEdit,
                    s.clipEdit,
                    s.clipPose,
                    s.clipDel
                    )
            else:
                raise RuntimeError, "File was not made with %s!" % s.software.title()
        else:
            raise IOError, "File not found. %s" % path
    def characterEdit(s, char):
        print "edit char"
    def clipEdit(s, clip):
        print "editclip"
    def clipPose(s, clip):
        print "pose out clip"
    def clipDel(s, clip):
        print "delete clip!"

### TESTING
# import animCopy.view.maya as view
# import animCopy.model.maya as model
# import animCopy.i18n as i18n
# Main(i18n.en, view, model, "maya")
