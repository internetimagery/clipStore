# Timer for time intensive things.
# Created 18/10/15 Jason Dixon
# http://internetimagery.com

class Timer(object):
    verbose = False
    def __init__(s, name):
        from time import time
        s.time = time
        s.name = name
    def __enter__(s): s.start = s.time()
    def __exit__(s, *err):
        if s.verbose: print "%s...\t\tElapsed time: %sms." % (s.name, (s.time() - s.start) * 1000)
