import math
import sumpf
import nlsp.common.plots as plot


def sweepgenerator(sampling_rate=48000.0, length=2**10, start_frequency=20.0, stop_frequency=3000.0):
    channel = []
    for i in range(0,length):
        channel.append(math.sin(2*math.pi*round((length*start_frequency)/math.log((stop_frequency/start_frequency),math.e))*
                                (math.exp((start_frequency*i)/round(length*start_frequency/math.log((stop_frequency/start_frequency),math.e))))))
    signal = sumpf.Signal(channels=(channel,),samplingrate=sampling_rate,labels=("Sweep"))
    plot.plot_groupdelayandmagnitude(sumpf.modules.FourierTransform(signal).GetSpectrum(),save=False,name="sweepfreqandphase")


sweepgenerator()