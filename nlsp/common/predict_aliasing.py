
def predictoutputfreq_usingsamplingtheory(frequency,max_harm,samplingrate):
    """
    predicts the aliasing frequency produced by nonlinear system
    :param frequency: the input frequency of pure sine wave to the system
    :param max_harm: the max harmonics produced by the nonlinear system
    :param samplingrate: the sampling rate of the system
    :return: the output frequencies which will be produced by the nonlinear system for given frequency and maximum
                harmonic order
    """
    x = []
    for sample in range(-max_harm,max_harm+1,1):
        x.extend([(sample*2*samplingrate/2-frequency,sample*samplingrate+frequency)])
    freq_duplicates = sorted(x)
    if max_harm%2 == 0:
        harm_order = [x for x in range(max_harm) if x%2 == 0]
        harm_order.append(max_harm)
    else:
        harm_order = [x for x in range(max_harm) if x%2 == 1]
        harm_order.append(max_harm)
    f = []
    for freq in freq_duplicates:
        for harm in harm_order:
            f.append(freq[0]-(harm-1)*frequency)
            f.append(freq[1]+(harm-1)*frequency)
    h = filter(lambda x: x>-10 and x<24000,sorted(f))
    h = list(set(h))
    return h

