import math
import sumpf
import numpy
import nlsp
import common.plot as plot

def mean_squared_error(input_signalorspectrum, output_signalorspectrum):
    """
    Calculates the mean of squares of error of two signals.
    This function calculates the mean square error in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum
    :param identified_signal: the array of identified signal or spectrum
    :return: the array of mean squared error of given signals or spectrums
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
    mse = []
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
            signal = observed - identified
            mse.append(numpy.mean(numpy.square(signal.GetChannels())**2))
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
    return mse

def squared_error(input_signalorspectrum, output_signalorspectrum):
    """
    Calculates the squares of error of two signals.
    This function calculates the squares of error in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum
    :param identified_signal: the array of identified signal or spectrum
    :return: the squared error signal
    """
    signal = []
    for observed,identified in zip(input_signalorspectrum,output_signalorspectrum):
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
            error = observed - identified
            signal.append(error * error)
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
    return signal

def signal_to_noise_ratio(input_signalorspectrum, output_signalorspectrum):
    """
    Calculates the Signal to Noise Ratio of the input and output signals of the model
    :param input_signalorspectrum: the input signal or spectrum
    :param output_signalorspectrum: the output signal or spectrum
    :return: the signal to noise ratio between the input and output
    """
    if isinstance(input_signalorspectrum,sumpf.Spectrum):
        input = sumpf.modules.InverseFourierTransform(input_signalorspectrum).GetSignal()
    else:
        input = input_signalorspectrum
    if isinstance(output_signalorspectrum,sumpf.Spectrum):
        output = sumpf.modules.InverseFourierTransform(output_signalorspectrum).GetSignal()
    else:
        output = output_signalorspectrum
    noise =  input - output
    noise_energy = nlsp.calculateenergy(noise)
    input_energy =  nlsp.calculateenergy(input)
    snr = 10*math.log10(input_energy[0]/noise_energy[0])
    return snr

def signal_to_noise_ratio_range(input_signalorspectrum, output_signalorspectrum, freq_range):
    """
    Calculates the Signal to Noise ratio between the range of frequencies
    :param input_signalorspectrum: the input signal or spectrum
    :param output_signalorspectrum: the output signal or spectrum
    :param freq_range: the range of frequencies over which the SNR has to be calculated
    :return: the signal to noise ratio between the input and output
    """
    if isinstance(input_signalorspectrum, sumpf.Signal):
        input_spec = sumpf.modules.FourierTransform(signal=input_signalorspectrum).GetSpectrum()
    else:
        input_spec = input_signalorspectrum
    if isinstance(output_signalorspectrum, sumpf.Signal):
        output_spec = sumpf.modules.FourierTransform(signal=output_signalorspectrum).GetSpectrum()
    else:
        output_spec = output_signalorspectrum
    input_spec_m = nlsp.cut_spectrum(input_spec,freq_range)
    output_spec_m = nlsp.cut_spectrum(output_spec,freq_range)
    snr = nlsp.signal_to_noise_ratio(input_spec_m,output_spec_m)
    return snr

def mean_squared_error_range(input_signalorspectrum, output_signalorspectrum, freq_range):
    """
    Calculates the mean of squares of error of two signals.
    This function calculates the mean square error in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum
    :param identified_signal: the array of identified signal or spectrum
    :return: the array of mean squared error of given signals or spectrums
    """
    if isinstance(input_signalorspectrum, sumpf.Signal):
        input_spec = sumpf.modules.FourierTransform(signal=input_signalorspectrum).GetSpectrum()
    else:
        input_spec = input_signalorspectrum
    if isinstance(output_signalorspectrum, sumpf.Signal):
        output_spec = sumpf.modules.FourierTransform(signal=output_signalorspectrum).GetSpectrum()
    else:
        output_spec = output_signalorspectrum
    input_spec_m = nlsp.cut_spectrum(input_spec,freq_range)
    output_spec_m = nlsp.cut_spectrum(output_spec,freq_range)
    mse = nlsp.mean_squared_error(input_spec_m,output_spec_m)
    return mse