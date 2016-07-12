import collections
import sumpf
import nlsp
from .hammerstein_model import HammersteinModel

class AliasingCompensatedHM_lowpass(HammersteinModel):
    """
    This class is derived from HammersteinModel class. This compensates the aliasing problem of the HammersteinModel.
    In this aliasing compensated Hammerstein model, a lowpass filter is used to compensate the aliasing.
    The cut-off frequency of the lowpass filter is chosen based on the degree of the polynomials used in nonlinear block.
    It uses sumpf modules to do the signal processing stuff.
    """
    def __init__(self, input_signal=None,
                 nonlin_func=nlsp.NonlinearFunction.power_series(1),
                 max_harm=1,
                 filter_impulseresponse=None,
                 filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                 attenuation=50.0):
        """
        :param input_signal: the input signal
        :param nonlin_func: the nonlinear function
        :param filter_impulseresponse: the impulse response of the linear filter block
        :param filterorder: the order of the filter function used to lowpass the signal
        :param filterfunction: the type of filter used for lowpass operation. eg. sumpf.modules.FilterGenerator.BUTTERWORTH(order=100}
        :param attenuation: the attenuation required at the cutoff frequency
        """

        self._filterfunction = filterfunction
        self._filterorder = self._filterfunction.GetOrder()
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
        super(AliasingCompensatedHM_lowpass, self).__init__(input_signal=input_signal,
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
        """
        Set the maximum order of harmonics produced by the nonlinear function. The aliasing compensation is performed
        based on this value.
        :param max_harmonic: the maximum order of harmonics introduced by the nonlinear function
        """
        self._max_harmonic = max_harmonic
        self._nonlin_function.SetMaximumHarmonic(max_harmonic)

    @sumpf.Output(float)
    def _GetMaximumHarmonic(self):
        return self._nonlin_function.GetMaximumHarmonic()

    @sumpf.Output(float)
    def _GetCutoffFrequency(self):
        # return ((self._ampsignal.GetOutput().GetSamplingRate()/2.0)/self._GetMaximumHarmonic())/\
        #        (2.0**((20.0*math.log(self._attenuation,10))/(6.0*self._filterorder)))
        return ((self._ampsignal.GetOutput().GetSamplingRate()/2.0)/self._GetMaximumHarmonic())\
               /(2.0**(self._attenuation/(6.0*self._filterorder)))

    @sumpf.Output(sumpf.Signal)
    def GetNLOutput(self):
        """
        Gets the output of the nonlinear block of the Hammerstein model.
        :return: the output of the nonlinear block of the Hammerstein model
        """
        return self._nonlin_function.GetOutput()
