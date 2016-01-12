import numpy
import sumpf
import nlsp
import common
import tkMessageBox

def AliasingTest():
    for frequency in range(1000,24000,1000):
        max_harm = 6
        samplingrate = 48000.0
        length = samplingrate
        gen = sumpf.modules.SineWaveGenerator(frequency=frequency,
                                              phase=0.0,
                                              samplingrate=samplingrate,
                                              length=length)
        harm_energy = []
        sig_energy = []
        gen_spec = sumpf.modules.FourierTransform(signal=gen.GetSignal())
        h_model = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=gen.GetSignal(),
                                                                nonlin_func=nlsp.NonlinearFunction.power_series(max_harm))
        h_sig = h_model.GetOutput()
        if max_harm %2 == 0:
            constant_signal = sumpf.modules.ConstantSignalGenerator(value=float(max_harm/2),samplingrate=h_sig.GetSamplingRate()
                                                                    ,length=h_sig.GetDuration()*h_sig.GetSamplingRate()).GetSignal()
            h_sig = h_sig-constant_signal
        h_spec = sumpf.modules.FourierTransform(signal=h_sig).GetSpectrum()
        channels_h = []
        channels_s = []
        for harmonics in range(0,max_harm+1,1):
            for c in h_spec.GetChannels():
                channel_h = []
                channel_s = []
                channel_z = []
                for i, s in enumerate(c):
                    if i > frequency*harmonics-10 and i < frequency*harmonics+50:
                        channel_h.append(abs(s)**2)
                    channel_s.append(abs(s)**2)
                channels_h.append(tuple(channel_h))
                channels_s.append(tuple(channel_h))
            harm_energy.append(numpy.sum(channel_h))
            sig_energy.append(numpy.sum(channel_s))
        # sliced_harmonics = sumpf.Signal(channels=tuple(channels_h), labels=h_spec.GetLabels())
        # common.plot.log()
        # common.plot.plot(sliced_harmonics)
        # print sig_energy,harm_energy
        harm_signal_ratio = (numpy.sum(harm_energy)/sig_energy[0]*100)
        print "signalenergy: %d,harmonicsenergy: %s " %(sig_energy[0],', '.join(map(str, harm_energy)))
        print "Quality of the Model: %d%%" %harm_signal_ratio
        print "maximum harmonics:%d,frequency of input sine:%d" %(max_harm,frequency)
        print
        # common.plot.log()
        # common.plot.plot(gen_spec.GetSpectrum(),show=False)
        # common.plot.plot(h_spec,show=True)
        if harm_signal_ratio > 100:
            print "Harmonics Energy is %f times larger than Signal Energy" %(harm_signal_ratio/100.0)
            print
            # tkMessageBox.askokcancel('Aliasing error','This model produces aliasing at frequency')
            # common.plot.log()
            # common.plot.plot(gen_spec.GetSpectrum(),show=False)
            # common.plot.plot(h_spec,show=True)
        elif harm_signal_ratio < 90:
            print "Signal Energy is %f times larger than Hamonics Energy" %(harm_signal_ratio/100.0)
            print
            # tkMessageBox.askokcancel('Aliasing error','This model produces aliasing at frequency')
            # common.plot.log()
            # common.plot.plot(gen_spec.GetSpectrum(),show=False)
            # common.plot.plot(h_spec,show=True)

AliasingTest()

