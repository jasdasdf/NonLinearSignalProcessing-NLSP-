import sumpf
import numpy

def mean_squared_error(observed_signalorspectrum,identified_signalorspectrum):
    """
    Calculates the average of squares of the errors in identification.
    In the case of length conflict zeros are appended.
    :param observed_signal: the array of observed signal or spectrum from the nonlinear system
    :param identified_signal: the array of identified signal or spectrum from the system identification method
    :return: the array of mean squared error of given signal or spectrum
    """
    mse = []
    for observed,identified in zip(observed_signalorspectrum,identified_signalorspectrum):
        if isinstance(observed,(sumpf.Signal,sumpf.Spectrum)) and isinstance(observed,(sumpf.Signal,sumpf.Spectrum)):
            if type(observed) != type(identified):
                if isinstance(observed,sumpf.Spectrum):
                    observed = sumpf.modules.InverseFourierTransform(observed).GetSignal()
                else:
                    identified = sumpf.modules.InverseFourierTransform(identified).GetSignal()
            if isinstance(observed,sumpf.Signal):
                merged_signal = sumpf.modules.MergeSignals(signals=[observed,identified],
                                                   on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS).GetOutput()
                observed = sumpf.modules.SplitSignal(data=merged_signal,channels=[0]).GetOutput()
                identified = sumpf.modules.SplitSignal(data=merged_signal,channels=[1]).GetOutput()
            else:
                merged_spectrum = sumpf.modules.MergeSpectrums(spectrums=[observed,identified],
                                                   on_length_conflict=sumpf.modules.MergeSpectrums.FILL_WITH_ZEROS).GetOutput()
                observed = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[0]).GetOutput()
                identified = sumpf.modules.SplitSpectrum(data=merged_spectrum,channels=[1]).GetOutput()
            signal = observed - identified
            mse.append(numpy.mean(numpy.square(signal.GetChannels())**2))
        else:
            print "The given arguments is not a sumpf.Signal or sumpf.Spectrum"
    return mse
