import nlsp

branches = range(5,11)

for branch in branches:
    try:
        print "Number of branches %r" %branch
        print
        nlsp.loudspeaker_evaluation_all(branch)
        # nlsp.db_evaluation_all(branch)
    except:
        print "exception occured"
