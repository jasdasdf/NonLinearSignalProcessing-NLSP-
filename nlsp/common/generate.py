import sumpf
import nlsp

def generate_puretones(frequencies,sampling_rate,length):
    """
    Generates pure tones with given frequencies, sampling rate and length
    :param frequencies: a tuple of frequencies
    :param sampling_rate: the sampling rate of the signal
    :param length: the length of the signal
    :return: a sine signal
    """
    ip_sine = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=sampling_rate,
                                                                 length=length).GetSignal()
    for freq in range(0,len(frequencies)):
        sine_signal = sumpf.modules.SineWaveGenerator(frequency=frequencies[freq],
                                              phase=0.0,
                                              samplingrate=sampling_rate,
                                              length=length)
        ip_sine = ip_sine + sine_signal.GetSignal()
    return ip_sine