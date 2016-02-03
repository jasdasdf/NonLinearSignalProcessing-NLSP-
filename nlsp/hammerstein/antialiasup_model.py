import sumpf
import nlsp
from .hammerstein_model import HammersteinModel
import collections

class AliasCompensatingHammersteinModelUpandDown(HammersteinModel):
    """
    A class which is derived from HammersteinModel class and this compensates the aliasing problem of the HammersteinModel.
    This extends the signal processing blocks of simple hammerstein model by upsampling the input signal prior to the
    nonlinear block and then downsampling at the end of the branch.
    It uses sumpf modules to do the signal processing stuff.
    """
    def __init__(self, input_signal=None, nonlin_func=nlsp.NonlinearFunction.power_series(1), max_harm=1,
                 filter_impulseresponse=None,
                 resampling_algorithm = sumpf.modules.ResampleSignal.SPECTRUM):
        """
        :param input_signal: the input signal instance to the Alias compensated Hammerstein model
        :param nonlin_func: the nonlinear function for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :param resampling_algorithm: the algorithm which can be used to downsample and upsample the signal
        :return:
        """
        # interpret the input parameters
        self._resampling_algorithm = resampling_algorithm

        # create the signal processing objects
        self._nonlin_function = nlsp.NonlinearFunction(nonlin_func = nonlin_func, max_harm = max_harm)
        self._prp = sumpf.modules.ChannelDataProperties()
        self._upsignal = sumpf.modules.ResampleSignal(algorithm=self._resampling_algorithm)
        self._upfilter = sumpf.modules.ResampleSignal(algorithm=self._resampling_algorithm)
        self._downoutput = sumpf.modules.ResampleSignal(algorithm=self._resampling_algorithm)
        self._attenuator = sumpf.modules.AmplifySignal()

        self.SetNLFunction = self._nonlin_function.SetNonlinearFunction

        # call the base classes constructor (which also calls _Connect)
        super(AliasCompensatingHammersteinModelUpandDown, self).__init__(input_signal=input_signal,
                                                                         nonlin_func=None,
                                                                         filter_impulseresponse=filter_impulseresponse)
        self.GetOutput = self._downoutput.GetOutput
        self.GetNLOutput = self._nonlin_function.GetOutput
        self.GetMaximumHarmonic = self._GetMaximumHarmonic

    def _Connect(self):
        sumpf.connect(self._ampsignal.GetOutput, self._prp.SetSignal)
        sumpf.connect(self._GetSamplingRate, self._upsignal.SetSamplingRate)
        sumpf.connect(self._GetSamplingRate, self._upfilter.SetSamplingRate)
        sumpf.connect(self._Getattenuation, self._attenuator.SetAmplificationFactor)
        sumpf.connect(self._ampsignal.GetOutput, self._upsignal.SetInput)
        sumpf.connect(self._ampfilter.GetOutput, self._upfilter.SetInput)
        sumpf.connect(self._upsignal.GetOutput,self._nonlin_function.SetInput)
        sumpf.connect(self._nonlin_function.GetOutput, self._attenuator.SetInput)
        sumpf.connect(self._attenuator.GetOutput, self._merger.AddInput)
        sumpf.connect(self._upfilter.GetOutput,self._merger.AddInput)
        sumpf.connect(self._merger.GetOutput,self._transform.SetSignal)
        sumpf.connect(self._transform.GetSpectrum,self._split1ch.SetInput)
        sumpf.connect(self._transform.GetSpectrum,self._split2ch.SetInput)
        sumpf.connect(self._split1ch.GetOutput,self._multiply.SetInput1)
        sumpf.connect(self._split2ch.GetOutput,self._multiply.SetInput2)
        sumpf.connect(self._multiply.GetOutput,self._itransform.SetSpectrum)
        sumpf.connect(self._itransform.GetSignal, self._downoutput.SetInput)
        sumpf.connect(self._prp.GetSamplingRate, self._downoutput.SetSamplingRate)



    @sumpf.Input(collections.Callable, ("_GetMaximumHarmonic", "_GetSamplingRate", "_Getattenuation"))
    def SetMaximumHarmonic(self, max_harmonic):
        self._max_harmonic = max_harmonic
        self._nonlin_function.SetMaximumHarmonic(max_harmonic)

    @sumpf.Output(float)
    def _GetMaximumHarmonic(self):
        return self._nonlin_function.GetMaximumHarmonic()

    @sumpf.Output(float)
    def _GetSamplingRate(self):
        return self._prp.GetSamplingRate()*self._GetMaximumHarmonic()

    @sumpf.Output(float)
    def _Getattenuation(self):
        return (1/float(self._GetMaximumHarmonic()))