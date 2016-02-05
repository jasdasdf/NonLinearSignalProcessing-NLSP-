import sumpf
import nlsp
import common

def find_frequencies(input,magnitude=100):
    """
    finds the frequencies in the input signal or spectrum
    :param input: the input signal or spectrum whose frequencies has to be found
    :param magnitude: the magnitude above which the frequency has to be detected
    :return: list of frequencies which are found in the input signal
    """
    if isinstance(input,(sumpf.Signal)):
        ip = sumpf.modules.FourierTransform(signal=input).GetSpectrum()
    else:
        ip = input
    frequencies = []
    for c in ip.GetChannels():
        channel_h = []
        for i, s in enumerate(c):
            if abs(s)**2 > magnitude:
                channel_h.append(i)
        frequencies.append(channel_h)
    h = [item for sublist in frequencies for item in sublist]
    frequency = []
    frequency[:] = [x / float(ip.GetResolution()) for x in h]
    return frequency