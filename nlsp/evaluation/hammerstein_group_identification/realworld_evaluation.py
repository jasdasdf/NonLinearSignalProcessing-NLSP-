import nlsp

branches = range(3,7)

for branch in branches:
    print "Number of branches %r" %branch
    print
    nlsp.loudspeaker_evaluation_all(branch)
