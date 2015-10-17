# Timer for time intensive things.
# Created 18/10/15 Jason Dixon
# http://internetimagery.com

from time import time

class Timer(object):
    verbose = False
    def __init__(s, name):
        s.name = name
    def __enter__(s): s.start = time()
    def __exit__(s, *err):
        if s.verbose: print "%s...\t\tElapsed time: %sms." % (s.name, (time() - s.start) * 1000)
