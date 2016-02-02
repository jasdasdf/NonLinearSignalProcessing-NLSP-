import math
import sumpf
import numpy
import nlsp

def mean_squared_error(observed_signalorspectrum, identified_signalorspectrum):
    """
    Calculates the mean of squares of error of two signals.
    This function calculates the mean square error in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum
    :param identified_signal: the array of identified signal or spectrum
    :return: the array of mean squared error of given signals or spectrums
    """
    if isinstance(observed_signalorspectrum, list) != True:
        observed_l = []
        observed_l.append(observed_signalorspectrum)
    else:
        observed_l = observed_signalorspectrum
    if isinstance(identified_signalorspectrum, list) != True:
        identified_l = []
        identified_l.append(identified_signalorspectrum)
    else:
        identified_l = identified_signalorspectrum
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

def squared_error(observed_signalorspectrum, identified_signalorspectrum):
    """
    Calculates the squares of error of two signals.
    This function calculates the squares of error in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum
    :param identified_signal: the array of identified signal or spectrum
    :return: the squared error signal
    """
    signal = []
    for observed,identified in zip(observed_signalorspectrum,identified_signalorspectrum):
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

def get_snr(input_signalorspectrum, output_signalorspectrum):
    """
    Calculates the Signal to Noise Ratio of the input and output signals of the model
    :param input_signalorspectrum:
    :param output_signalorspectrum:
    :return:
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
