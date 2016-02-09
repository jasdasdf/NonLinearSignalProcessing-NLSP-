import math
import numpy
import sumpf
import nlsp

def get_transfer_function(excitation, response):
    """
    Calculate the transfer function of the system
    :param excitation: the input signal to the system
    :param response: the output signal of the system
    :return: the transfer function of the system
    """
    fft = sumpf.modules.FourierTransform(signal=excitation)
    excitation_spectrum = fft.GetSpectrum()
    fft.SetSignal(response)
    response_spectrum = fft.GetSpectrum()
    sumpf.destroy_connectors(fft)
    rgi = sumpf.modules.RegularizedSpectrumInversion(spectrum=excitation_spectrum)
    regularized = rgi.GetOutput()
    sumpf.destroy_connectors(rgi)
    if len(regularized.GetChannels()) == 1 and  len(response_spectrum.GetChannels()) != 1:
        cpy = sumpf.modules.CopySpectrumChannels(input=regularized, channelcount=len(response_spectrum.GetChannels()))
        regularized = cpy.GetOutput()
        sumpf.destroy_connectors(cpy)
    cls = sumpf.modules.CopyLabelsToSpectrum(data_input=response_spectrum * regularized, label_input=response)
    relabeled = cls.GetOutput()
    sumpf.destroy_connectors(cls)
    return relabeled

def get_impulse_response(excitation, response):
    """
    Calculate the impulse response of the system
    :param excitation: the input signal to the system
    :param response: the output signal of the system
    :return: the impulse response of the system
    """
    transferfunction = get_transfer_function(excitation, response)
    ifft = sumpf.modules.InverseFourierTransform(spectrum=transferfunction)
    result = ifft.GetSignal()
    sumpf.destroy_connectors(ifft)
    return result

def get_sweep_harmonics_spectrum(excitation, response, sweep_start_freq, sweep_stop_freq, max_harm):
    """
    Calculate the spectrum of the harmonics of sweep based on farina method
    :param excitation: the excitation sweep of the system
    :param response: the response of the system
    :param sweep_start_freq: start frequency of the sweep signal
    :param sweep_stop_freq: stop frequency of the sweep signal
    :param max_harm: the maximum harmonics upto which the harmomics should be calculated
    :return: the sumpf spectrum of merged harmonic spectrums
    """
    impulse_response = get_impulse_response(excitation,response)
    linear = sumpf.modules.CutSignal(signal=impulse_response,start=0,stop=len(impulse_response)/2).GetOutput()
    merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    merger.AddInput(linear)
    for i in range(2,max_harm+1):
        harmonics = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=impulse_response, harmonic_order=i,
                                                              sweep_start_frequency=sweep_start_freq,
                                                              sweep_stop_frequency=sweep_stop_freq,
                                                              sweep_duration=len(excitation)/excitation.GetSamplingRate()).GetHarmonicImpulseResponse()
        merger.AddInput(sumpf.Signal(channels=harmonics.GetChannels(),
                                        samplingrate=excitation.GetSamplingRate(), labels=harmonics.GetLabels()))
    harmonics_spec = sumpf.modules.FourierTransform(merger.GetOutput()).GetSpectrum()
    return harmonics_spec

def get_sweep_harmonics_ir(excitation, response, sweep_start_freq, sweep_stop_freq, max_harm):
    """
    Calculate the harmonics of the sweep based on nonconvolution
    :param excitation: the excitation sweep of the system
    :param response: the response of the system
    :param sweep_start_freq: start frequency of the sweep signal
    :param sweep_stop_freq: stop frequency of the sweep signal
    :param max_harm: the maximum harmonics upto which the harmomics should be calculated
    :return: the sumpf signal of merged harmonic spectrums
    """
    impulse_response = get_impulse_response(excitation,response)
    linear = sumpf.modules.CutSignal(signal=impulse_response,start=0,stop=len(impulse_response)/2).GetOutput()
    merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    merger.AddInput(linear)
    for i in range(2,max_harm+1):
        harmonics = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=impulse_response,harmonic_order=i,sweep_start_frequency=sweep_start_freq,
                                                  sweep_stop_frequency=sweep_stop_freq,sweep_duration=len(excitation)).GetHarmonicImpulseResponse()
        merger.AddInput(harmonics)
    return merger.GetOutput()

def log_bpfilter(start_freq,stop_freq,branches,input):
    """
    Generates logarithmically seperated band pass filters between start and stop frequencies.
    :param start_freq: the start frequency of the bandpass filter
    :param stop_freq: the stop frequency of the bandpass filter
    :param branches: the number of branches of bandpass filter
    :param input: the input signal to get the filter parameters
    :return: a tuple of filter spectrums, and the list of frequencies
    """
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSignal(input)
    dummy = 10
    while True:
        dummy = dummy - 0.1
        low = 100 * (dummy**1)
        high = 100 * (dummy**branches)
        if low > start_freq*2 and high < stop_freq:
            break
    frequencies = []
    for i in range(1,branches+1):
        frequencies.append(100 * (dummy**i))
    filter_spec = []
    for freq in frequencies:
        spec =  (sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                            frequency=freq,
                                            resolution=ip_prp.GetResolution(),
                                            length=ip_prp.GetSpectrumLength()).GetSpectrum())*\
                (sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                            frequency=freq/2,transform=True,
                                            resolution=ip_prp.GetResolution(),
                                            length=ip_prp.GetSpectrumLength()).GetSpectrum())
        filter_spec.append(sumpf.modules.InverseFourierTransform(spec).GetSignal())
    return filter_spec

def append_zeros(signal, length=None):
    """
    Appends zeros until the signal has the given length. If no length is given,
    zeros will be appended until the length is a power of 2.
    """
    if length is None:
        length = 2 ** int(math.ceil(math.log(len(signal), 2)))
    zeros = length - len(signal)
    result = sumpf.Signal(channels=tuple([c + (0.0,) * zeros for c in signal.GetChannels()]),
                          samplingrate=signal.GetSamplingRate(),
                          labels=signal.GetLabels())
    return result

def cut_spectrum(inputspectrum,freq_range):
    """
    Appends zero outside the desired frequency range of the spectrum
    :param inputspectrum: the input spectrum to which zero has to be appended outside the desired frequency range
    :param freq_range: the desired freqency range
    :return: the modified spectrum
    """
    channels_ip = []
    for ip in inputspectrum.GetChannels():
        channel_ip = []
        channel_op = []
        for n,i in enumerate(ip):
            if n > freq_range[0]/inputspectrum.GetResolution() and n < freq_range[1]/inputspectrum.GetResolution():
                channel_ip.append(i)
            else:
                channel_ip.append(0.0)
                channel_op.append(0.0)
        channels_ip.append(tuple(channel_ip))
    input_spectrum = sumpf.Spectrum(channels=tuple(channels_ip), resolution=inputspectrum.GetResolution(),
                                  labels=inputspectrum.GetLabels())
    return input_spectrum

def relabel(input,labels):
    """
    Helper function to change the label of Sumpf signals and spectrums
    :param input: the tuple of signal or spectrum
    :param labels: the string which replaces the label of signal or spectrum
    :return: the relabelled signal or spectrum
    """
    if isinstance(input, list) != True:
        ip = []
        ip.append(input)
    else:
        ip = input
    if isinstance(labels, list) != True:
        label = []
        label.append(labels)
    else:
        label = labels
    outputs = []
    for inputs,labels in zip(ip, label):
        if isinstance(inputs, sumpf.Signal):
            relabler = sumpf.modules.RelabelSignal(input=inputs,labels=(labels,)).GetOutput()
        elif isinstance(inputs, sumpf.Spectrum):
            relabler = sumpf.modules.RelabelSpectrum(input=inputs,labels=(labels,)).GetOutput()
        else:
            print "The given input is not of Signal or Spectrum class"
        outputs.append(relabler)
    if len(outputs) == 1:
        outputs = outputs[0]
    else:
        outputs = outputs
    return outputs

def harmonicsvsall_energyratio(output_nlsystem,input,nl_order,sweep_start_freq,sweep_stop_freq,max_harm):
    harmonics = nlsp.get_sweep_harmonics_spectrum(input,output_nlsystem,sweep_start_freq,sweep_stop_freq,max_harm)
    all_energy = nlsp.calculateenergy_betweenfreq_time(harmonics,[sweep_start_freq+50,sweep_stop_freq-50])
    harm_energy = []
    for i in range(0,nl_order):
        harm_energy.append(all_energy[i])
    if nl_order % 2 == 0: # even
        harm_energy = harm_energy[1::2]
    else: # odd
        harm_energy = harm_energy[0::2]
    return numpy.divide(numpy.sum(all_energy),numpy.sum(harm_energy))