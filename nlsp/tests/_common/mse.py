import sumpf
import numpy

def mean_squared_error(observed_signalorspectrum,identified_signalorspectrum):
    """
    Calculates the mean of squares of error of two signals.
    This function calculates the mean square error in time domain. If the input is spectrum then it transforms it to
    time domain. And in the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum
    :param identified_signal: the array of identified signal or spectrum
    :return: the array of mean squared error of given signals or spectrums
    """
    mse = []
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
            signal = observed - identified
            mse.append(numpy.mean(numpy.square(signal.GetChannels())**2))
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
    return mse
