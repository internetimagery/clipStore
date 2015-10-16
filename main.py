# Lets run this thing!!
# Created 15/10/15 Jason Dixon
# http://internetimagery.com

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
        return dict((e, f) for e, f in dict( (a, dict((c, d) for c, d in b.items() if d) ) for a, b in data.items()).items() if f)

    def sendFiles(s, path=None):
        """
        Given user input path, list character files in a dir.
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
            char.data.update(**new)
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
        if char.data:
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
        else:
            raise RuntimeError, "There is no stored selection to make clips from."

    def clipCaptureThumbs(s, char, clip, camera, frameRange):
        """
        Load up thumbnails
        """
        if not len(frameRange) == 2: raise RuntimeError, "Invalid frame range %s" % frameRange
        frameNum = frameRange[1] - frameRange[0] # Number of frames
        thumbSize = 200
        stepSize = 3 # 5 # Size to jump across frames

        if not frameNum: # Single pose
            thumbs = [s.model.thumb.capture(thumbSize, camera, frameRange[0])]
        elif frameNum < stepSize * 2: # Short clip. Any less and less than 3 images are created.
            thumbs = [
                s.model.thumb.capture(thumbSize, camera, frameRange[0]),
                s.model.thumb.capture(thumbSize, camera, frameRange[0] + frameNum * 0.5),
                s.model.thumb.capture(thumbSize, camera, frameRange[1])
                ]
        else: # Long clip
            step = int(frameNum / stepSize) # Roughly every 5 frames.
            inc = float(frameNum) / step
            thumbs = [s.model.thumb.capture(thumbSize, camera, a * inc + frameRange[0]) for a in range(0, step+1)]
        clip.thumbs = thumbs

    def clipCaptureData(s, char, clip, frames):
        """
        Capture Data
        Accepts =
            frames = [ frameStart, frameEnd ]
        Insert into clip = { object : { attribute : [val1, val2, val3, ... ]} }
        """
        if len(frames) == 2:
            named = s.flipData(char, char.data) # Convert to real names
            capture = s.model.clip.capture(named, frames) # Capture all data
            clip.data.update(**s.flipData(char, capture)) # Revert data to ID's
        else:
            raise RuntimeError, "Invalid range given."

    def clipRun(s, char, clip, include=False, ignore=False):
        """
        Run the clip! Finally!!
        if include, only run on what is selected.
        if ignore, run on everything that is not selected.
        """
        charData = s.filterData(char.data) # Pull out our base data
        # Filter off clip data to our match our character base data
        data = dict( (a, dict( (c, d) for c, d in b.items() if c in charData[a] )) for a, b in clip.data.items() if a in charData )
        data = s.flipData(char, data) # Switch to real names
        selection = s.filterData(s.model.selection.current()) # Grab current selection
        # Filter out data live!
        if include and ignore:
            raise AttributeError, "You cannot use both include and ignore at the same time."
        elif include:
            data = dict( (a, dict( (c, data[a][c]) for c, d in b.items() if c in data[a] ) ) for a, b in selection.items() if a in data )
        elif ignore:
            data =dict( (e, f) for e, f in dict( (a, dict( (c, d) for c, d in b.items() if a not in selection or c not in selection[a] ) ) for a, b in data.items() ).items() if f)
        s.model.clip.replay(data) # FINALLY after all this craziness. Lets pose out our animation!
