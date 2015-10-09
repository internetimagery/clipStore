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
        print "new char"
    def characterLoad(s, path):
        """
        Open an existing character!
        """
        print "opening char", path


### TESTING
# import animCopy.view.maya as view
# import animCopy.model.maya as model
# import animCopy.i18n as i18n
# Main(i18n.en, view, model, "maya")
