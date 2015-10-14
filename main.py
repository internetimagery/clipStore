# Lets run this thing!!
from pprint import pprint
import character
import os.path
import os

class Main(object):
    def __init__(s, i18n, view, model, software):
        s.i18n = i18n
        s.view = view
        s.model = model
        s.software = software

        s.ext = ".clips" # File extension!

        # Load our Selector window
        view.selector(
            s.i18n,
            s.sendFiles,
            s.characterNew,
            s.characterLoad
            )

    def flipData(s, char, data):
        """
        Given a structure of data. Flip the ID's and Real names.
        Structure { object : { attribute : None } }
        """
        return dict((char.ref[a], dict((char.ref[c], d) for c, d in b.items())) for a, b in data.items())

    def filterData(s, data):
        """
        Filter out empty attributes and objects from Data
        Strcuture { object : { attribute : True/False } }
        """
        return dict((e, f) for e, f in dict( (a, [c for c, d in b.items() if d] ) for a, b in data.items()).items() if f)

    def sendFiles(s, path=None):
        """
        Given user input path, list character files
        """
        if not path:
            path = s.view.fileDialog(s.i18n).openDir()
        if path:
            path = os.path.realpath(path)
            return [os.path.join(path, f) for f in os.listdir(path) if s.ext in f]

    # CHARACTER RELATED STUFF!

    def characterNew(s):
        """
        Create a new character!
        """
        path = s.view.fileDialog(s.i18n).save()
        if path:
            if os.path.isfile(path): os.remove(path)
            char = s.characterLoad(path)

    def characterLoad(s, path):
        """
        Open an existing character!
        Accepts = "path/to/file"
        """
        path = os.path.realpath(path)
        char = character.Character(path, s.software)
        if char.metadata["software"] == s.software:
            s.view.clips(
                s.i18n,
                char,
                s.characterEdit,
                s.clipEdit,
                s.clipCacheThumbs,
                s.clipRun
                )
            return char
        else:
            raise RuntimeError, "File was not made with %s!" % s.software.title()

    def characterEdit(s, char, refresh):
        """
        Open the character editing window.
        """
        s.view.characterEdit(
            s.i18n,
            char,
            s.characterRetarget,
            s.characterSendData,
            s.characterAddObjects,
            s.characterEditAttributes,
            s.characterRemoveObject,
            refresh
            )

    def characterRetarget(s, char):
        """
        Open the character retarget window.
        """
        s.view.characterRetarget(
            s.i18n,
            char,
            s.characterEdit,
            s.characterSendData,
            s.characterEditReference
            )

    def characterSendData(s, char):
        """
        Prepare data. Replacing references with actual names.
        Sending = { object : attribute : True/False }
        """
        return s.flipData(char, char.data)

    def characterAddObjects(s, char):
        """
        Add some new objects / attributes to the character from selection
        """
        selection = s.model.selection.current() # Grab current selection.
        if selection:
            # Grab all inactive attributes so we can skip them in the adding process
            exclusions = set([c for a, b in char.data.items() for c, d in b.items() if not d])
            # Create new entry
            new = dict((a, dict((c, False if c in exclusions else True) for c in b)) for a, b in selection.items() if a not in char.data)
            # Convert entry to ID's
            new = s.flipData(char, new)
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

    def characterEditReference(s, char, old, new):
        """
        Change a reference to to point from one object to another.
        """
        oldID = char.ref[old]
        char.ref[oldID] = new


    # CLIPS STUFF HERE !!

    def clipEdit(s, char, refresh, clip=None):
        """
        Load the clip edit window. If no existing clip is specified. Create a new one.
        """
        if not clip: # No clip specified? Make one!
            clip = char.createClip()

        s.view.clipEdit(
            s.i18n,
            char,
            clip,
            s.clipCaptureThumbs,
            s.characterSendData,
            s.clipCaptureData,
            refresh
            )

    def clipCacheThumbs(s, char, clip):
        """
        Pull out thumbs for use
        Return = [ thumb1, thumb2, ... ]
        """
        imgs = clip.metadata.get("thumbs", False)
        if imgs:
            return [char.cache(imgs[a]) for a in sorted(imgs.keys())]
        return ["savePaintSnapshot.png"]

    def clipCaptureThumbs(s, char, clip, camera, frameRange):
        """
        Load up thumbnails
        """
        if not len(frameRange) == 2: raise RuntimeError, "Invalid frame range %s" % frameRange
        frameNum = frameRange[1] - frameRange[0] # Number of frames
        thumbSize = 200

        if not frameNum: # Single pose
            thumbs = { 1 : s.model.captureThumb(thumbSize, camera, frameRange[0]) }
        elif frameNum <= 5: # Short clip
            thumbs = {
                1 : s.model.captureThumb(thumbSize, camera, frameRange[0]),
                2 : s.model.captureThumb(thumbSize, camera, frameRange[0] + frameNum * 0.5),
                3 : s.model.captureThumb(thumbSize, camera, frameRange[1])
                }
        else: # Long clip
            step = int(frameNum / 5) # Roughly every 5 frames.
            inc = float(frameNum) / step
            thumbs = dict( (a+1, s.model.captureThumb(thumbSize, camera, a * inc + frameRange[0])) for a in range(0, step+1) )
        clip.metadata["thumbs"] = thumbs

    def clipCaptureData(s, char, clip, frames):
        """
        Capture Data
        Accepts =
            data = { objects : { attribtes : True/False } }
            frames = [ frameStart, frameEnd ]
        Insert into clip = { object : { attribute : [val1, val2, val3, ... ]} }
        """
        if len(frames) == 2:
            # Trim out "false" attributes, create { object : [ attribute1, attribute2, ... ] }
            filteredData = dict( (a, [c for c, d in b.items() if d] ) for a, b in s.characterSendData(char).items())
            data = s.model.captureClip(filteredData, frames)
            # Revert the data back into ID's
            clip.clip = dict((char.ref[a], dict((char.ref[c], d) for c, d in b.items())) for a, b in data.items())
        else:
            raise RuntimeError, "Invalid range given."

    def clipRun(s, char, clip, include=False, ignore=False):
        """
        Run the clip! Finally!!
        if include, only run on what is selected.
        if ignore, run on everything that is not selected.
        """
        data = dict((char.ref[a], dict((char.ref[c], d) for c, d in b.items())) for a, b in clip.clip.items())
        selection = s.model.selection.current()
        if include and ignore: raise AttributeError, "You cannot use both include and ignore at the same time."
        if include:
            print "only include selection"
        elif ignore:
            print "ignore selection"
        print "running clip"
        print "data", data
        print "selection", selection


### TESTING
# import animCopy.view.maya as view
# import animCopy.model.maya as model
# import animCopy.i18n as i18n
# Main(i18n.en, view, model, "maya")
