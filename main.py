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

    # CHARACTER RELATED STUFF!

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
        Accepts = "path/to/file"
        """
        path = os.path.realpath(path)
        if os.path.isfile(path):
            char = character.Character(path, s.software)
            if char.metadata["software"] == s.software:
                s.view.clips(
                    s.i18n["clips"],
                    char,
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
        """
        Open the character editing window.
        """
        s.view.characterEdit(
            s.i18n["characterEdit"],
            char,
            s.characterRetarget,
            s.characterSendData,
            s.characterAddObjects,
            s.characterEditAttributes,
            s.characterRemoveObject
            )

    def characterRetarget(s, char):
        """
        Open the character retarget window.
        """
        raise NotImplementedError, "Not yet built. Sorry... :("

    def characterSendData(s, char):
        """
        Prepare data. Replacing references with actual names.
        Sending = { object : attribute : True/False }
        """
        return dict((char.ref[a], dict((char.ref[c], d) for c, d in b.items())) for a, b in char.data.items())

    def characterAddObjects(s, char, objects):
        """
        Add some new objects / attributes to the character
        Accepts = { object : [attribute1, attribute2, ... ] }
        """
        if objects:
            # Grab all inactive attributes so we can skip them in the adding process
            exclusions = set([c for a, b in char.data.items() for c, d in b.items() if not d])
            # Create new entry
            new = dict((char.ref[a], dict((char.ref[c], False if char.ref[c] in exclusions else True) for c in b)) for a, b in objects.items() if a not in char.data)
            # Add entry to existing data
            char.data = dict(char.data, **new)
        else: raise RuntimeError, "Nothing selected."

    def characterRemoveObject(s, char, obj):
        """
        Remove a given object.
        Accepts = "Object"
        """
        obj = char.ref[obj]
        if obj in char.data:
            del char.data[obj]
        else:
            raise RuntimeError, "Object not in collection."

    def characterEditAttributes(s, char, enable, attr, obj=None):
        """
        Enable or Disable attributes. Singuarly if "obj" specified, otherwise in bulk.
        Accepts =
            enable = True/False
            attr = "attributename"
            obj = "objectname" or nothing
        """
        attr = char.ref[attr]
        obj = char.ref[obj] if obj else None
        for o, attrs in char.data.items():
            if not obj or o == obj:
                for at in attrs:
                    if at == attr:
                        char.data[o][at] = enable

    # CLIPS STUFF HERE !!

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
