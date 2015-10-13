import os
import os.path

class Temp_Path(str):
  def __del__(s):
      print "DONE"
  # def __getattribute__(s, k):
  #     raise AttributeError, "\"Temp_Path\" cannot be modified with \"%s\"" % k

p = Temp_Path("here")
c = p.replace("h", "r")
print p, c
