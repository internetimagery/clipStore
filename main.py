# Lets run this thing!!

class Main(object):
    def __init__(s, i18n, view, model, software):
        s.i18n = i18n
        s.view = view
        s.model = model
        s.software = software
        print "lets go"



### TESTING
import animCopy.view.maya as view
import animCopy.model.maya as model
import animCopy.i18n.en as i18n
Main(i18n, view, model, "maya")
