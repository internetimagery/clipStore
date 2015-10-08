# Load images in file
import os
import sys
import os.path
root = os.path.join(os.path.dirname(__file__))
pics = [os.path.realpath(os.path.join(root, f)) for f in os.listdir(root) if f[-3:] in set(["png"])]
class Files(object): pass
img = Files()
img.small = pics[-1]
img.large = pics[0]
sys.modules[__name__] = img
