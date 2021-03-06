import sumpf
import numpy
import nlsp

def mean_squared_error_time(input_signalorspectrum, output_signalorspectrum):
    """
    Calculates the mean of squares of error of two signals.
    This function calculates the mean square error in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param input_signalorspectrum: the array of input signal or spectrum
    :param output_signalorspectrum: the array of output signal or spectrum
    :return: the array of mean squared error between input and output
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

def mean_squared_error_time_range(input_signalorspectrum, output_signalorspectrum, freq_range):
    """
    Calculates the mean of squares of error of two signals.
    This function calculates the mean square error in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum
    :param identified_signal: the array of identified signal or spectrum
    :return: the array of mean squared error of given signals or spectrums
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
    mse = nlsp.mean_squared_error_time(input_spec_m,output_spec_m)
    return mse

def mean_squared_error_freq(input_signalorspectrum, output_signalorspectrum):
    """
    Calculates the mean of squares of error of two spectrums.
    This function calculates the mean square error in frequency domain. If the input is signal then it transforms it to
    frequency domain. And in the case of length conflict zeros are appended.
    :param input_signalorspectrum: the array of input spectrum
    :param output_signalorspectrum: the array of output spectrum
    :return: the array of mean squared error of two spectrums
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
            if isinstance(observed,sumpf.Signal):
                observed = sumpf.modules.FourierTransform(observed).GetSpectrum()
            if isinstance(identified,sumpf.Signal):
                identified = sumpf.modules.FourierTransform(identified).GetSpectrum()
            if len(observed) != len(identified):
                merged_spectrum = sumpf.modules.MergeSpectrums(spectrums=[observed,identified],
                                                   on_length_conflict=sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS).GetOutput()
                observed = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[0]).GetOutput()
                identified = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[1]).GetOutput()
            error = observed - identified
            mse.append(numpy.mean(abs((numpy.square(error.GetChannels())))))
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
    return mse

def mean_squared_error_freq_range(input_signalorspectrum, output_signalorspectrum, freq_range):
    """
    Calculates the mean of squares of error of two spectrums.
    This function calculates the mean square error in frequency domain. If the input is signal then it transforms it to
    frequency domain. And in the case of length conflict zeros are appended.
    :param input_signalorspectrum: the array of input spectrum
    :param output_signalorspectrum: the array of output spectrum
    :return: the array of mean squared error of the spectrums
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
    mse = nlsp.mean_squared_error_freq(input_spec_m,output_spec_m)
    return mse
