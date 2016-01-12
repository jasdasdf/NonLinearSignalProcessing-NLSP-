import numpy
import sumpf
import nlsp
import common
import tkMessageBox

def AliasingTest():
    for frequency in range(1000,23000,1000):
        max_harm = 5
        samplingrate = 48000.0
        length = samplingrate
        gen = sumpf.modules.SineWaveGenerator(frequency=frequency,
                                              phase=0.0,
                                              samplingrate=samplingrate,
                                              length=length)
        harm_energy = []
        sig_energy = []
        gen_spec = sumpf.modules.FourierTransform(signal=gen.GetSignal())
        h_sig = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=gen.GetSignal(),nonlin_func=nlsp.NonlinearFunction.power_series(max_harm))
        h_spec = sumpf.modules.FourierTransform(signal=h_sig.GetOutput()).GetSpectrum()
        for harmonics in range(1,max_harm+1,1):
            channels_h = []
            channels_s = []
            for c in h_spec.GetChannels():
                channel_h = []
                channel_s = []
                for s in enumerate(c):
                    if s[0] > frequency*harmonics-30 and s[0] < frequency*harmonics+30:
                        channel_h.append(abs(s[1])**2)
                    channel_s.append(abs(s[1])**2)
                channels_h.append(tuple(channel_h))
                channels_s.append(tuple(channel_h))
            harm_energy.append(numpy.sum(channel_h))
            sig_energy.append(numpy.sum(channel_s))
        # inputspec = sumpf.Spectrum(channels=tuple(channels_h), labels=h_spec.GetLabels())
        # outputspec = sumpf.Signal(channels=tuple(channels_s), labels=h_spec.GetLabels())
        # common.plot.log()
        # common.plot.plot(inputspec)
        # common.plot.plot(outputspec)
        print sig_energy,harm_energy
        print sig_energy[0],numpy.sum(harm_energy)
        print numpy.sum(harm_energy)/sig_energy[0]
        if numpy.sum(harm_energy)/sig_energy[0] < 0.9:
            tkMessageBox.askokcancel('Aliasing error','This model produces aliasing at frequency')
            common.plot.log()
            common.plot.plot(gen_spec.GetSpectrum(),show=False)
            common.plot.plot(h_spec,show=True)

AliasingTest()

