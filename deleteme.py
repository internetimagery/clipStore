import threading
import maya.utils as utils

def running(text):
    print "RUNNING %s" % text


def go():
    try:
        # utils.executeDeferred(lambda: running("deferred 1"))
        utils.executeInMainThreadWithResult(running, "result 1")
        # utils.executeDeferred(lambda: running("deferred 2"))
        # utils.executeInMainThreadWithResult(running, "result 2")
    except:
        pass

threading.Thread(target=go).start()
