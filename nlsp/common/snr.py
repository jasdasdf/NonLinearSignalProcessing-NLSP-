import math
import sumpf
import nlsp

def signal_to_noise_ratio_time(input_signalorspectrum, output_signalorspectrum):
    """
    Calculates the signal to noise ratio between two signals
    This function calculates the signal to noise ratio in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param input_signalorspectrum: the array of input signal or spectrum
    :param output_signalorspectrum: the array of output signal or spectrum
    :return: the array of signal to noise ratio between input and output
    """
    if isinstance(input_signalorspectrum, list) != True:
        observed_l = []
        observed_l.append(input_signalorspectrum)
    else:
        observed_l = input_signalorspectrum
    if isinstance(output_signalorspectrum, list) != True:
        identified_l = []
        identified_l.append(output_signalorspectrum)
    else:
        identified_l = output_signalorspectrum
    snr = []
    for observed,identified in zip(observed_l,identified_l):
        if isinstance(observed,(sumpf.Signal,sumpf.Spectrum)) and isinstance(observed,(sumpf.Signal,sumpf.Spectrum)):
            if isinstance(observed,sumpf.Spectrum):
                observed = sumpf.modules.InverseFourierTransform(observed).GetSignal()
            if isinstance(identified,sumpf.Spectrum):
                identified = sumpf.modules.InverseFourierTransform(identified).GetSignal()
            if len(observed) != len(identified):
                merged_signal = sumpf.modules.MergeSignals(signals=[observed,identified],
                                                   on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS).GetOutput()
                observed = sumpf.modules.SplitSignal(data=merged_signal,channels=[0]).GetOutput()
                identified = sumpf.modules.SplitSignal(data=merged_signal,channels=[1]).GetOutput()
            noise = observed - identified
            noise_energy = nlsp.calculateenergy_time(noise)
            input_energy =  nlsp.calculateenergy_time(observed)
            snr.append(10*math.log10(input_energy[0]/noise_energy[0]))
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
    return snr

def signal_to_noise_ratio_time_range(input_signalorspectrum, output_signalorspectrum, time_range):
    """
    Calculates the signal to noise ratio between two signals.
    This function calculates the signal to noise ratio in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum
    :param identified_signal: the array of identified signal or spectrum
    :return: the array of signal to noise ratio of given signals or spectrums
    """
    if isinstance(input_signalorspectrum, list) != True:
        ip = []
        ip.append(input_signalorspectrum)
    else:
        ip = input_signalorspectrum
    if isinstance(output_signalorspectrum, list) != True:
        op = []
        op.append(output_signalorspectrum)
    else:
        op = output_signalorspectrum
    input_sig_m = []
    output_sig_m = []
    for input_signalorspectrum,output_signalorspectrum in zip(ip,op):
        if isinstance(input_signalorspectrum, sumpf.Spectrum):
            input_sig = sumpf.modules.InverseFourierTransform(input_signalorspectrum).GetSignal()
        else:
            input_sig = input_signalorspectrum
        if isinstance(output_signalorspectrum, sumpf.Spectrum):
            output_sig = sumpf.modules.InverseFourierTransform(output_signalorspectrum).GetSignal()
        else:
            output_sig = output_signalorspectrum
        input_sig_m.append(sumpf.modules.CutSignal(signal=input_sig,start=time_range[0],stop=time_range[1]).GetOutput())
        output_sig_m.append(sumpf.modules.CutSignal(signal=output_sig,start=time_range[0],stop=time_range[1]).GetOutput())
    snr = nlsp.signal_to_noise_ratio_time(input_sig_m,output_sig_m)
    return snr

def signal_to_noise_ratio_freq(input_signalorspectrum, output_signalorspectrum):
    """
    Calculates the signal to noise ratio of two spectrums.
    This function calculates the signal to noise ratio in frequency domain. If the input is signal then it transforms it
    to frequency domain. And in the case of length conflict zeros are appended.
    :param input_signalorspectrum: the array of input spectrum
    :param output_signalorspectrum: the array of output spectrum
    :return: the array of signal to noise ratio of two spectrums
    """
    if isinstance(input_signalorspectrum, list) != True:
        observed_l = []
        observed_l.append(input_signalorspectrum)
    else:
        observed_l = input_signalorspectrum
    if isinstance(output_signalorspectrum, list) != True:
        identified_l = []
        identified_l.append(output_signalorspectrum)
    else:
        identified_l = output_signalorspectrum
    snr = []
    for observed,identified in zip(observed_l,identified_l):
        if isinstance(observed,(sumpf.Signal,sumpf.Spectrum)) and isinstance(observed,(sumpf.Signal,sumpf.Spectrum)):
            if isinstance(observed,sumpf.Signal):
                observed = sumpf.modules.FourierTransform(observed).GetSpectrum()
            if isinstance(identified,sumpf.Signal):
                identified = sumpf.modules.FourierTransform(identified).GetSpectrum()
            if len(observed) != len(identified):
                merged_spectrum = sumpf.modules.MergeSpectrums(spectrums=[observed,identified],
                                                   on_length_conflict=sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS).GetOutput()
                observed = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[0]).GetOutput()
                identified = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[1]).GetOutput()
            noise = observed - identified
            noise_energy = nlsp.calculateenergy_freq(noise)
            input_energy =  nlsp.calculateenergy_freq(observed)
            snr.append(10*math.log10(input_energy[0]/noise_energy[0]))
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
    return snr

def signal_to_noise_ratio_freq_range(input_signalorspectrum, output_signalorspectrum, freq_range):
    """
    Calculates the signal to noise ratio of two spectrums.
    This function calculates the signal to noise ratio in frequency domain. If the input is signal then it transforms it
    to frequency domain. And in the case of length conflict zeros are appended.
    :param input_signalorspectrum: the array of input spectrum
    :param output_signalorspectrum: the array of output spectrum
    :return: the signal to noise ratio of two spectrums
    """
    if isinstance(input_signalorspectrum, list) != True:
        ip = []
        ip.append(input_signalorspectrum)
    else:
        ip = input_signalorspectrum
    if isinstance(output_signalorspectrum, list) != True:
        op = []
        op.append(output_signalorspectrum)
    else:
        op = output_signalorspectrum
    input_spec_m = []
    output_spec_m = []
    for input_signalorspectrum,output_signalorspectrum in zip(ip,op):
        if isinstance(input_signalorspectrum, sumpf.Signal):
            input_spec = sumpf.modules.FourierTransform(signal=input_signalorspectrum).GetSpectrum()
        else:
            input_spec = input_signalorspectrum
        if isinstance(output_signalorspectrum, sumpf.Signal):
            output_spec = sumpf.modules.FourierTransform(signal=output_signalorspectrum).GetSpectrum()
        else:
            output_spec = output_signalorspectrum
        input_spec_m.append(nlsp.cut_spectrum(input_spec,freq_range))
        output_spec_m.append(nlsp.cut_spectrum(output_spec,freq_range))
    snr = nlsp.signal_to_noise_ratio_freq(input_spec_m,output_spec_m)
    return snr

def snr(input_signalorspectrum,output_signalorspectrum,type=3,freqrange=[20,20000],plot=False,show=False,label=None):
    if isinstance(input_signalorspectrum, list) != True:
        observed_l = []
        observed_l.append(input_signalorspectrum)
    else:
        observed_l = input_signalorspectrum
    if isinstance(output_signalorspectrum, list) != True:
        identified_l = []
        identified_l.append(output_signalorspectrum)
    else:
        identified_l = output_signalorspectrum
    snr = []
    for observed,identified in zip(observed_l,identified_l):
        if isinstance(observed,(sumpf.Signal,sumpf.Spectrum)) and isinstance(observed,(sumpf.Signal,sumpf.Spectrum)):
            if isinstance(observed,sumpf.Signal):
                observed = sumpf.modules.FourierTransform(observed).GetSpectrum()
            if isinstance(identified,sumpf.Signal):
                identified = sumpf.modules.FourierTransform(identified).GetSpectrum()
            if len(observed) != len(identified):
                merged_spectrum = sumpf.modules.MergeSpectrums(spectrums=[observed,identified],
                                                   on_length_conflict=sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS).GetOutput()
                observed = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[0]).GetOutput()
                identified = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[1]).GetOutput()
            reference = observed
            reference = nlsp.cut_spectrum(reference,freqrange)
            identified = nlsp.cut_spectrum(identified,freqrange)
            if type == 1:
                reference_energy = nlsp.calculateenergy_betweenfreq_freq(reference,freqrange)
                identified_energy = nlsp.calculateenergy_betweenfreq_freq(identified,freqrange)
                noise_energy = abs(reference_energy[0] - identified_energy[0])
                snr.append(10*math.log10(identified_energy[0]/noise_energy))
            elif type == 2:
                noise =  reference - identified
                noise_energy = nlsp.calculateenergy_betweenfreq_freq(noise,freqrange)
                input_energy = nlsp.calculateenergy_betweenfreq_freq(identified,freqrange)
                snr.append(10*math.log10(input_energy[0]/noise_energy[0]))
            elif type == 3:
                noise =  reference - identified
                div = identified / noise
                if plot is True:
                    if label is None:
                        label = "Noise"
                    nlsp.common.plots.relabelandplot(noise/identified,label,show=show)
                div_energy = nlsp.calculateenergy_betweenfreq_freq(div,freqrange)
                snr.append(10*math.log10(div_energy[0]))
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
    return snr