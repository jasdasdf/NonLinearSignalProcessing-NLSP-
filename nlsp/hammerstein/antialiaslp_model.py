import collections
import sumpf
import nlsp
from .hammerstein_model import HammersteinModel
import common
import math

class AliasCompensatingHammersteinModelLowpass(HammersteinModel):
    """
    A class to generate the output of the Aliasing compensated Hammerstein model.
    This extends the functionality of simple hammerstein model by introducing a lowpass filter prior to applying nonlinear function
    on the input signal.
    It imports the sumpf modules to do the signal processing functions.
    """
    def __init__(self, input_signal=None, nonlin_func=nlsp.NonlinearFunction.power_series(1), max_harm=1,
                 filter_impulseresponse=None, filterorder=20,
                 filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=20),
                 attenuation=0.0001):
        """
        :param input_signal: the input signal instance to the Alias compensated Hammerstein model
        :param nonlin_func: the nonlinear function-instance for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :param filterorder: the order of the filter function used to lowpass the signal
        :param filterfunction: the type of filter used for lowpass operation. eg. BUTTERWORTH,CHEBYSHEV1,CHEBYSHEV2 etc
        :param attenuation: the attenuation of the cutoff frequency
        :return:
        """

        self._filterorder = filterorder
        self._filterfunction = filterfunction
        self._attenuation = attenuation
        self._nonlin_function = nlsp.NonlinearFunction(nonlin_func = nonlin_func, max_harm = max_harm)
        self._max_harmonic = self._nonlin_function.GetMaximumHarmonic()
        self._prp = sumpf.modules.ChannelDataProperties()
        self._lpfilter = sumpf.modules.FilterGenerator(filterfunction=self._filterfunction)
        self._lptransform = sumpf.modules.FourierTransform()
        self._lpitransform = sumpf.modules.InverseFourierTransform()
        self._lpmultiply = sumpf.modules.MultiplySpectrums()

        self.SetNLFunction = self._nonlin_function.SetNonlinearFunction

        # call the base classes constructor (which also calls _Connect)
        super(AliasCompensatingHammersteinModelLowpass, self).__init__(input_signal=input_signal,
                                                                         nonlin_func=None,
                                                                         filter_impulseresponse=filter_impulseresponse)
        self.GetOutput = self._itransform.GetSignal
        self.GetNLOutput = self._nonlin_function.GetOutput
        self.GetMaximumHarmonic = self._GetMaximumHarmonic

    def _Connect(self):
        sumpf.connect(self._ampsignal.GetOutput, self._prp.SetSignal)
        sumpf.connect(self._prp.GetResolution, self._lpfilter.SetResolution)
        sumpf.connect(self._prp.GetSpectrumLength, self._lpfilter.SetLength)
        sumpf.connect(self._GetCutoffFrequency, self._lpfilter.SetFrequency)
        sumpf.connect(self._lpfilter.GetSpectrum,self._lpmultiply.SetInput1)
        sumpf.connect(self._ampsignal.GetOutput, self._lptransform.SetSignal)
        sumpf.connect(self._lptransform.GetSpectrum, self._lpmultiply.SetInput2)
        sumpf.connect(self._lpmultiply.GetOutput, self._lpitransform.SetSpectrum)
        sumpf.connect(self._lpitransform.GetSignal, self._nonlin_function.SetInput)
        sumpf.connect(self._nonlin_function.GetOutput, self._merger.AddInput)
        sumpf.connect(self._ampfilter.GetOutput, self._merger.AddInput)
        sumpf.connect(self._merger.GetOutput, self._transform.SetSignal)
        sumpf.connect(self._transform.GetSpectrum, self._split1ch.SetInput)
        sumpf.connect(self._transform.GetSpectrum, self._split2ch.SetInput)
        sumpf.connect(self._split1ch.GetOutput, self._multiply.SetInput1)
        sumpf.connect(self._split2ch.GetOutput, self._multiply.SetInput2)
        sumpf.connect(self._multiply.GetOutput, self._itransform.SetSpectrum)

    @sumpf.Input(collections.Callable, ("_GetMaximumHarmonic", "_GetCutoffFrequency"))
    def SetMaximumHarmonic(self, max_harmonic):
        self._max_harmonic = max_harmonic
        self._nonlin_function.SetMaximumHarmonic(max_harmonic)

    @sumpf.Output(float)
    def _GetMaximumHarmonic(self):
        return self._nonlin_function.GetMaximumHarmonic()

    @sumpf.Output(float)
    def _GetCutoffFrequency(self):
        return ((self._ampsignal.GetOutput().GetSamplingRate()/2)/self._GetMaximumHarmonic())/\
               (2**(20*math.log(self._attenuation,10)/(6*self._filterorder)))
