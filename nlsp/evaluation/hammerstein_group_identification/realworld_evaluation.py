import nlsp

branches = range(1,6,1)

for branch in branches:
    print "Number of branches %r" %branch
    print
    nlsp.loudspeaker_evaluation_all(branch)
    nlsp.distortionbox_evaluation_all(branch)
