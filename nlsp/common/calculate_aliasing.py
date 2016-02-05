import sumpf
import nlsp
import numpy

def calculate_aliasing_percentage(input,output,ip_frequency,max_harm):
    """
    this function calculates the percentage of aliasing produced by the model
    :param input: the input signal which should be a pure sine wave of particular frequency
    :param output: the output of the model
    :param ip_frequency: the frequency of the pure sine wave which is given to the model
    :param max_harm: the max harmonics produced by the model
    :return: the percentage of aliasing found in the output of the system, in the case of perfect model it returns zero
    and the value increaces with increase in aliasing effect
    """
    for frequency in range(19000,25000,100):
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
        h_spec = sumpf.modules.FourierTransform(signal=h_sig).GetSpectrum()
        channels_h = []
        channels_s = []
        for harmonics in range(0,max_harm+1,1):
            for c in h_spec.GetChannels():
                channel_h = []
                channel_s = []
                for i, s in enumerate(c):
                    if i > frequency*harmonics-10 and i < frequency*harmonics+50:
                        channel_h.append(abs(s)**2)
                    channel_s.append(abs(s)**2)
                channels_h.append(tuple(channel_h))
                channels_s.append(tuple(channel_h))
            harm_energy.append(numpy.sum(channel_h))
            sig_energy.append(numpy.sum(channel_s))
        harm_signal_ratio = (numpy.sum(harm_energy)/sig_energy[0]*100)
        print harm_signal_ratio

