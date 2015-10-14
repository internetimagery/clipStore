
# range 1 ... 45
# 1, 5, 10, 15, 20, 25, 30, 35, 40, 45 !!

# Diff = max - min : 44 # Full range the frames cover
# Step = int(Diff / 5) : 8 # How many steps to take, to make each chunk 5 rounded down
# Inc = Diff / Step : Given number of steps, how large is each step?

def printR(r):
    Diff = (r[1] - r[0]) # Number of frames in that range inclusive
    print "diff", Diff
    step = int(Diff / 5) # How many steps will be in the range? Near enough?
    print "step", step
    inc = float(Diff) / step # How large is each step?
    print "inc", inc
    print [a * inc + r[0] for a in range(0, step + 1)]
    # for i in range(1, diff + 1):
    #     print i

print "--- 1, 45"
printR([1, 45])
print "--- 5, 32"
printR([5, 32])
print "--- 61, 82"
printR([61, 82])
