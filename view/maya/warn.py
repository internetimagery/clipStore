# Visual popup on errors. Not an error handler!
# Created 11/10/15 Jason Dixon
# http://internetimagery.com

import maya.cmds as cmds
import traceback
import sys

class Safe(object):
    def _err(s, title, message):
        cmds.confirmDialog(
            t="Uh oh... %s" % title,
            m=message
        )
    def run(s, *args, **kwargs):
        with Safe:
            if len(args) and callable(args[0]):
                return args[0](*args[1:], **kwargs)
            else:
                raise RuntimeError, "Function not provided as first argument."
    def __enter__(s):
        pass
    def __exit__(s, *err):
        if err:
            s._err(err[0].__name__, err[1].message)
Safe = Safe()
