import math
import numpy
import random
import sumpf
import nlsp
import common.plot as plot

def get_transfer_function(excitation, response, start_freq=20.0, stop_freq=20000.0):
    """
    Calculate the transfer function of the system
    :param excitation: the input signal to the system
    :param response: the output signal of the system
    :param start_freq: the start frequency of the input
    :param stop_freq: the stop frequency of the input
    :return: the transfer function of the system
    """
    fft = sumpf.modules.FourierTransform(signal=excitation)
    excitation_spectrum = fft.GetSpectrum()
    fft.SetSignal(response)
    response_spectrum = fft.GetSpectrum()
    sumpf.destroy_connectors(fft)
    rgi = sumpf.modules.RegularizedSpectrumInversion(spectrum=excitation_spectrum,start_frequency=start_freq,
                                                     stop_frequency=stop_freq)
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

def get_impulse_response(excitation, response, start_freq, stop_freq):
    """
    Calculate the impulse response of the system
    :param excitation: the input signal to the system
    :param response: the output signal of the system
    :param start_freq: the start frequency
    :param stop_freq: the stop frequency
    :return: the impulse response of the system
    """
    transferfunction = get_transfer_function(excitation, response, start_freq, stop_freq)
    ifft = sumpf.modules.InverseFourierTransform(spectrum=transferfunction)
    result = ifft.GetSignal()
    sumpf.destroy_connectors(ifft)
    return result

def get_sweep_harmonics_spectrum(excitation, response, sweep_start_freq, sweep_stop_freq, sweep_length, max_harm):
    """
    Calculate the spectrum of the harmonics of sweep based on farina method
    :param excitation: the excitation sweep of the system
    :param response: the response of the system
    :param sweep_start_freq: start frequency of the sweep signal
    :param sweep_stop_freq: stop frequency of the sweep signal
    :param max_harm: the maximum harmonics upto which the harmomics should be calculated
    :return: the sumpf spectrum of merged harmonic spectrums
    """
    if sweep_length is None:
        sweep_length = len(excitation)
    impulse_response = get_impulse_response(excitation,response,sweep_start_freq,sweep_stop_freq)
    linear = sumpf.modules.CutSignal(signal=impulse_response,start=0,stop=len(impulse_response)/4).GetOutput()
    linear = nlsp.relabel(nlsp.append_zeros(linear),"1 hamonic")
    merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    merger.AddInput(linear)
    for i in range(2,max_harm+1):
        harmonics = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=impulse_response, harmonic_order=i,
                                                              sweep_start_frequency=sweep_start_freq,
                                                              sweep_stop_frequency=sweep_stop_freq,
                                                              sweep_duration=(sweep_length/excitation.GetSamplingRate())).GetHarmonicImpulseResponse()
        harmonics = nlsp.relabel(harmonics,"%d harmonic"%i)
        merger.AddInput(sumpf.Signal(channels=harmonics.GetChannels(),
                                        samplingrate=excitation.GetSamplingRate(), labels=harmonics.GetLabels()))
    harmonics_spec = sumpf.modules.FourierTransform(merger.GetOutput()).GetSpectrum()
    return harmonics_spec

def get_sweep_harmonics_ir(sweep_generator, response, max_harm=None):
    """
    Calculate the harmonics of the sweep based on nonconvolution
    :param excitation: the excitation sweep of the system
    :param response: the response of the system
    :param sweep_start_freq: start frequency of the sweep signal
    :param sweep_stop_freq: stop frequency of the sweep signal
    :param max_harm: the maximum harmonics upto which the harmomics should be calculated
    :return: the sumpf signal of merged harmonic spectrums
    """
    sweep_length = sweep_generator.GetLength()
    excitation = sweep_generator.GetOutput()
    sweep_start_freq = sweep_generator.GetStartFrequency()
    sweep_stop_freq = sweep_generator.GetStopFrequency()
    if sweep_length is None:
        sweep_length = len(excitation)
    if max_harm is None:
        max_harm = 5
    impulse_response = get_impulse_response(excitation,response,sweep_start_freq,sweep_stop_freq)
    linear = sumpf.modules.CutSignal(signal=impulse_response,start=0,stop=len(impulse_response)/4).GetOutput()
    linear = nlsp.relabel(nlsp.append_zeros(linear),"1 hamonic")
    merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    merger.AddInput(linear)
    for i in range(2,max_harm+1):
        harmonics = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=impulse_response, harmonic_order=i,
                                                              sweep_start_frequency=sweep_start_freq,
                                                              sweep_stop_frequency=sweep_stop_freq,
                                                              sweep_duration=(sweep_length/excitation.GetSamplingRate())).GetHarmonicImpulseResponse()
        harmonics = nlsp.relabel(harmonics,"%d harmonic"%i)
        merger.AddInput(sumpf.Signal(channels=harmonics.GetChannels(),
                                        samplingrate=excitation.GetSamplingRate(), labels=harmonics.GetLabels()))
    harmonics_ir = merger.GetOutput()
    return harmonics_ir

def log_bpfilter(start_freq=20.0,stop_freq=20000.0,branches=5,input=sumpf.Signal(),amplify=False):
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
        if amplify is True:
            spec = sumpf.modules.AmplifySpectrum(input=spec,factor=random.randint(10,100)).GetOutput()
        filter_spec.append(sumpf.modules.InverseFourierTransform(spec).GetSignal())
    # filter_spec = [i for i in reversed(filter_spec)]
    return filter_spec

def create_bpfilter(frequencies,input):
    """
    Generates bandpass filters with given frequencies.
    :param frequencies: the tuple of frequencies
    :param input: the input signal to get the filter parameters
    :return: a tuple of filter spectrums, and the list of frequencies
    """
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSignal(input)
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

def get_mean(ip):
    energy_allchannels = []
    for c in ip.GetChannels():
        energy_singlechannel = []
        c = reversed(c)
        for i,s in enumerate(c):
            # energy_singlechannel.append((abs(s)**2)*(1*(dummy**i)))
            energy_singlechannel.append(s)
        #energy_allchannels.append(numpy.average(energy_singlechannel,weights=range(1,len(energy_singlechannel)+1).reverse()))
        energy_allchannels.append(numpy.divide(numpy.sum(energy_singlechannel),len(c)))
    return energy_allchannels

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

def relabel(input,labels=None):
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

def harmonicsvsall_energyratio(output_nlsystem,input,nl_order,sweep_start_freq,sweep_stop_freq,sweep_duration,max_harm):
    """
    Calculates the energy ratio between the desired and undesired harmonics in power series expansion
    :param output_nlsystem: the output sweep of the nonlinear system
    :param input: the input sweep to the nonlinear system
    :param nl_order: the order of nonlinear system
    :param sweep_start_freq: the sweep start frequency
    :param sweep_stop_freq: the sweep stop frequency
    :param max_harm: the maximum harmonics upto which the energy has to be compared
    :return: the ratio between the energy of desired harmonics and all harmonics
    """
    if sweep_duration is None:
        sweep_duration = len(input)/input.GetSamplingRate()
    harmonics = nlsp.get_sweep_harmonics_spectrum(input,output_nlsystem,sweep_start_freq,sweep_stop_freq,sweep_duration,max_harm)
    all_energy = nlsp.calculateenergy_betweenfreq_time(harmonics,[sweep_start_freq+50,sweep_stop_freq-50])
    harm_energy = []
    for i in range(0,nl_order):
        harm_energy.append(all_energy[i])
    if nl_order % 2 == 0: # even
        harm_energy = harm_energy[1::2]
    else: # odd
        harm_energy = harm_energy[0::2]
    return numpy.divide(numpy.sum(harm_energy),numpy.sum(all_energy))

def nl_branches(function,branches):
    """
    Generates array of nonlinear functions for hammerstein group model
    :param function: the nonlinear function
    :param branches: number of branches
    :return: the array of nonlinear functions
    """
    nl = []
    for i in range(1,branches+1):
        nl.append(function(i))
    return nl

def add_noise(signal,distribution):
    """
    Helper function to add signal and noise
    :param signal: the input signal
    :param distribution: the distribution of noise, should be a method of sumpf.modules.NoiseGenerator
    :return: the added noise and input signal
    """
    noise = sumpf.modules.NoiseGenerator(distribution=distribution,
                                         samplingrate=signal.GetSamplingRate(),
                                         length=len(signal)).GetSignal()
    signal_and_noise = sumpf.modules.AddSignals(signal1=signal, signal2=noise).GetOutput()
    return signal_and_noise

def binomial(x, y):
    try:
        binom = math.factorial(x) // math.factorial(y) // math.factorial(x - y)
    except ValueError:
        binom = 0
    return binom

def get_nl_impulse_response(sweep_generator,response):
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(response).GetSpectrum()
    out_spec = out_spec / response.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()
    return ir_sweep

def get_nl_harmonics(sweep_generator,response,harmonics):
    sweep_length = sweep_generator.GetLength()
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(response).GetSpectrum()
    out_spec = out_spec / response.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_sweep_direct = nlsp.relabel(ir_sweep_direct,"Reference Harmonics 1")
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)
    for i in range(harmonics-1):
        split_harm = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=ir_sweep,
                                                            harmonic_order=i+2,
                                                            sweep_generator=sweep_generator).GetHarmonicImpulseResponse()
        split_harm = sumpf.modules.CutSignal(signal=split_harm,stop=len(sweep_generator.GetOutput())).GetOutput()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=("Reference Harmonics %r"%(i+2),)))
    tf = sumpf.modules.FourierTransform(ir_merger.GetOutput()).GetSpectrum()
    return tf

def get_nl_harmonics_iden(sweep_generator,response,harmonics):
    sweep_length = sweep_generator.GetLength()
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(response).GetSpectrum()
    out_spec = out_spec / response.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_sweep_direct = nlsp.relabel(ir_sweep_direct,"Identified Harmonics 1")
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)
    for i in range(harmonics-1):
        split_harm = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=ir_sweep,
                                                            harmonic_order=i+2,
                                                            sweep_generator=sweep_generator).GetHarmonicImpulseResponse()
        split_harm = sumpf.modules.CutSignal(signal=split_harm,stop=len(sweep_generator.GetOutput())).GetOutput()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=("Identified Harmonics %r"%(i+2),)))
    tf = sumpf.modules.FourierTransform(ir_merger.GetOutput()).GetSpectrum()
    return tf

def harmonicsvsall_energyratio_nl(sweep_generator,response,degree):

    harmonics = nlsp.get_nl_harmonics(sweep_generator,response,degree)
    all_energy = nlsp.calculateenergy_freq(harmonics)
    harm_energy = []
    for i in range(0,degree):
        harm_energy.append(all_energy[i])
    if degree % 2 == 0: # even
        harm_energy = harm_energy[1::2]
    else: # odd
        harm_energy = harm_energy[0::2]
    return numpy.divide(numpy.sum(harm_energy),numpy.sum(all_energy))

def dot_product(signal1=None,signal2=None):
    if signal1 is None:
        signal1 = sumpf.Signal()
    if signal2 is None:
        signal2 = sumpf.Signal()
    product = sumpf.modules.MultiplySignals(signal1=signal1,signal2=signal2).GetOutput()
    energy_allchannels = []
    for c in product.GetChannels():
        energy_singlechannel = []
        for s in c:
            energy_singlechannel.append(abs(s)**2)
        energy_allchannels.append(numpy.sum(energy_singlechannel))
    return energy_allchannels