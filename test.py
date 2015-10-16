import os
import os.path

class Temp_Path(str):
    _ok = set(["rfind"])
    def __del__(s):
        print "Done"
    def __getattribute__(s, k):
        raise AttributeError, "\"Temp_Path\" cannot be modified with \"%s\"" % k

# Example Usage
# import tempfile
# with tempfile.NamedTemporaryFile(delete=False) as f: path = Temp_Path(f.name)
# print path
p = Temp_Path("stuff/thing.cone")
print os.path.splitext(p)
