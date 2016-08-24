import matplotlib.pyplot as plot

def robustness_with_addednoise():
    x = [0,0.5,0.7,1.0]
    linear = [65,65,64,63]
    linearHGM = [64,57,56,54]
    powersweep = [71,60,56,53]
    chebysweep = [69,57,55,53]
    adaptive = [67,64,63,61]
    sweepadaptive = [65,62,62,62]
    miso = [50,50,50,50]
    wienerg = [47,47,47,47]
    plot.plot(x, linear, label="linear", marker='o')
    plot.plot(x,linearHGM, label="linear-HGM", marker='v')
    plot.plot(x,powersweep, label="power-sweep", marker='^')
    plot.plot(x,chebysweep, label="cheby-sweep", marker='<')
    plot.plot(x,adaptive, label="adaptive", marker='>')
    plot.plot(x,sweepadaptive, label="sweep-adaptive", marker='p')
    plot.plot(x,miso, label="MISO", marker='s')
    plot.plot(x,wienerg, label="Wiener-G", marker='h')
    plot.xlabel("Variance of the noise")
    plot.ylabel("Accuracy (SER) [dB]")
    plot.legend(loc='best', fancybox=True, framealpha=0.5)
    plot.ylim([42,72])
    plot.xlim([-0.25,1.25])
    plot.show()

def identification_complexity_numberofbranches():
    x = [2,3,4,5]
    linear = [0.08,0.08,0.08,0.08]
    linearHGM = [0.14,0.18,0.25,0.31]
    powersweep = [0.14,0.18,0.25,0.31]
    chebysweep = [0.08,0.08,0.09,0.09]
    adaptive = [23.3,36.9,48.8,60.1]
    sweepadaptive = [24.1,37.5,49.1,61.3]
    miso = [0.5,1.2,2.1,3.5]
    wienerg = [0.17,0.2,0.3,0.44]
    plot.semilogy(x, linear, label="linear", marker='o')
    plot.semilogx(x,linearHGM, label="linear-HGM", marker='v')
    plot.plot(x,powersweep, label="power-sweep", marker='^')
    plot.plot(x,chebysweep, label="cheby-sweep", marker='<')
    plot.plot(x,adaptive, label="adaptive", marker='>')
    plot.plot(x,sweepadaptive, label="sweep-adaptive", marker='p')
    plot.plot(x,miso, label="MISO", marker='s')
    plot.plot(x,wienerg, label="Wiener-G", marker='h')
    plot.xlabel("Number of branches of resulting model")
    plot.ylabel("Identification time [s]")
    plot.legend(loc='best', fancybox=True, framealpha=0.5)
    plot.ylim([-0.5,85])
    plot.xlim([1,6])
    plot.show()

def identification_complexity_excitationlength():
    x = [2**14,2**15,2**16,2**17]
    linear = [0.02,0.04,0.08,0.16]
    linearHGM = [0.02,0.04,0.09,0.17]
    powersweep = [0.04,0.08,0.16,0.31]
    chebysweep = [0.04,0.09,0.19,0.39]
    wienerg = [0.06,0.13,0.25,0.53]
    miso = [0.27,0.53,1.18,2.34]
    adaptive = [8.62,17.4,41.7,83.2]
    sweepadaptive = [8.75,18.6,41.9,83.1]
    plot.semilogy(x, linear, label="linear", marker='o')
    plot.semilogx(x,linearHGM, label="linear-HGM", marker='v')
    plot.plot(x,powersweep, label="power-sweep", marker='^')
    plot.plot(x,chebysweep, label="cheby-sweep", marker='<')
    plot.plot(x,adaptive, label="adaptive", marker='>')
    plot.plot(x,sweepadaptive, label="sweep-adaptive", marker='p')
    plot.plot(x,miso, label="MISO", marker='s')
    plot.plot(x,wienerg, label="Wiener-G", marker='h')
    plot.xlabel("Excitation length [number of samples]")
    plot.ylabel("Identification time [s]")
    plot.legend(loc='best', fancybox=True, framealpha=0.5)
    plot.ylim([0.0,85])
    plot.xlim([2**13,2**17+8192])
    plot.show()

# robustness_with_addednoise()
# identification_complexity_excitationlength()
identification_complexity_numberofbranches()