import sumpf
import nlsp
import numpy

def calculateenergy_time(input):
    """
    Calculates the energy of the input in time domain
    :param input: the input signal or spectrum whose energy has to be calculated, it should be a sumpf.Signal() or
     sumpf.Spectrum datatype and it can contain multiple channels
    :return: the tuple of the energy of the input signal of different channels
    """
    if isinstance(input,(sumpf.Spectrum)):
        ip = sumpf.modules.InverseFourierTransform(spectrum=input).GetSignal()
    else:
        ip = input
    energy_allchannels = []
    for c in ip.GetChannels():
        energy_singlechannel = []
        for s in c:
            energy_singlechannel.append(abs(s)**2)
        energy_allchannels.append(numpy.sum(energy_singlechannel))
    return energy_allchannels

def calculateenergy_freq(input):
    """
    Calculates the energy of the input in frequency domain
    :param input: the input signal or spectrum whose energy has to be calculated, it should be a sumpf.Signal() or
     sumpf.Spectrum datatype and it can contain multiple channels
    :return: the tuple of the energy of the input spectrum of different channels
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
    Calculates the energy of input signal at certain frequencies in freq domain
    :param input: the input signal or spectrum whose energy has to be calculated
    :param frequencies: the array of frequencies at which the energy has to be calculated
    :return: the tuple of the energy of input spectrum in frequency domain
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

def calculateenergy_betweenfreq_freq(input,frequency_range):
    """
    Calculates the energy of input signal between certain frequencies of input signal
    :param input: the input signal or spectrum whose energy has to be calculated
    :param frequency_range: the range of frequencies over which the energy has to be calculated
    :return: the tuple of the energy of input spectrum in frequency domain
    """
    if isinstance(input,(sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input).GetSpectrum()
    else:
        ip = input
    spec = nlsp.cut_spectrum(ip,frequency_range)
    energy = nlsp.calculateenergy_freq(spec)
    return energy

def calculateenergy_betweenfreq_time(input,frequency_range):
    """
    Calculates the energy of input signal between certain frequencies of input signal
    :param input: the input signal or spectrum whose energy has to be calculated
    :param frequency_range: the range of frequencies over which the energy has to be calculated
    :return: the tuple of the energy of input spectrum in time domain
    """
    if isinstance(input,(sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input).GetSpectrum()
    else:
        ip = input
    spec = nlsp.cut_spectrum(ip,frequency_range)
    energy = nlsp.calculateenergy_time(spec)
    return energy