import sumpf
import nlsp
import numpy

def calculateenergy(input):
    """
    Calculates the energy of the input signal
    :param signal: the input signal whose energy has to be calculated, it should be a sumpf.Signal() or
     sumpf.Spectrum datatype and it can contain multiple channels
    :return: the tuple of the energy of the input signal of different channels
    """
    if isinstance(input,(sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input).GetSpectrum()
    else:
        ip = input
    energy_allchannels = []
    for c in ip.GetChannels():
        energy_singlechannel = []
        for s in c:
            energy_singlechannel.append(abs(s)**2)
        energy_allchannels.append(numpy.sum(energy_singlechannel))
    return energy_allchannels

def calculateenergy_atparticularfrequencies(input,frequencies):
    """
    Calculates the energy of input signal at certain frequencies
    :param input: the input signal or spectrum whose energy has to be calculated
    :param frequencies: the array of frequencies at which the energy has to be calculated
    :return:
    """
    if isinstance(input,(sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input).GetSpectrum()
    else:
        ip = input
    energy = []
    frequency = []
    frequency[:] = [x / float(ip.GetResolution()) for x in frequencies]
    for frequency in frequency:
        channels_h = []
        for c in ip.GetChannels():
            channel_h = []
            for i,s in enumerate(c):
                if i > frequency-50 and i < frequency+50:
                    channel_h.append(abs(s)**2)
            channels_h.append(tuple(channel_h))
        energy.append(numpy.sum(channels_h))
    return energy