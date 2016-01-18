import sumpf
import nlsp
from .hammerstein_model import HammersteinModel
import collections

class AliasCompensatingHammersteinModelUpandDown(HammersteinModel):
    """
    A class to generate the output of the Aliasing compensated Hammerstein model.
    This extends the functionality of simple hammerstein model by upsampling the input signal to the Hammerstein model and the
    downsampling is done at different positions.
    It imports the sumpf modules to do the signal processing functions.
    """
    def __init__(self, input_signal=None, nonlin_func=lambda x:x, max_harm=1,
                 filter_impulseresponse=None, downsampling_position=None,
                 resampling_algorithm = sumpf.modules.ResampleSignal.SPECTRUM):
        """
        :param input_signal: the input signal instance to the Alias compensated Hammerstein model
        :param nonlin_func: the nonlinear function-instance for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :param downsampling_position: the downsampling position, It is a integer value which may be 1,2,3 for downsampling after nonlinear
                                    signal block, after the linear filter block, after the summation of the hammerstein model signals
                                    respectively. It this parameter is not given then the downsampling is done at the end
        :param resampling_algorithm: the algorithm which can be used to downsample and upsample the signal
        :return:
        """
        # interpret the input parameters
        self._downsampling_position = downsampling_position
        self._resampling_algorithm = resampling_algorithm
        self._nonlin_function = nonlin_func
        # self._max_harmonic = nonlin_func.GetMaximumHarmonic()

        # create the signal processing objects
        self._prp = sumpf.modules.ChannelDataProperties()
        self._upsignal = sumpf.modules.ResampleSignal(algorithm=self._resampling_algorithm)
        self._upfilter = sumpf.modules.ResampleSignal(algorithm=self._resampling_algorithm)

        self.SetNLFunction = self._nonlin_function.SetNonlinearFunction

        # call the base classes constructor (which also calls _Connect)
        super(AliasCompensatingHammersteinModelUpandDown, self).__init__(input_signal=input_signal,
                                                                         nonlin_func=None,
                                                                         filter_impulseresponse=filter_impulseresponse)
        self.GetOutput = self._itransform.GetSignal
        self.GetNLOutput = self._nonlin_function.GetOutput
        self.GetMaximumHarmonic = self._GetMaximumHarmonic

    def _Connect(self):
        sumpf.connect(self._ampsignal.GetOutput, self._prp.SetSignal)
        sumpf.connect(self._GetSamplingRate, self._upsignal.SetSamplingRate)
        sumpf.connect(self._GetSamplingRate, self._upfilter.SetSamplingRate)
        sumpf.connect(self._ampsignal.GetOutput, self._upsignal.SetInput)
        sumpf.connect(self._ampfilter.GetOutput, self._upfilter.SetInput)
        sumpf.connect(self._upsignal.GetOutput,self._nonlin_function.SetInput)
        sumpf.connect(self._nonlin_function.GetOutput,self._merger.AddInput)
        sumpf.connect(self._upfilter.GetOutput,self._merger.AddInput)
        sumpf.connect(self._merger.GetOutput,self._transform.SetSignal)
        sumpf.connect(self._transform.GetSpectrum,self._split1ch.SetInput)
        sumpf.connect(self._transform.GetSpectrum,self._split2ch.SetInput)
        sumpf.connect(self._split1ch.GetOutput,self._multiply.SetInput1)
        sumpf.connect(self._split2ch.GetOutput,self._multiply.SetInput2)
        sumpf.connect(self._multiply.GetOutput,self._itransform.SetSpectrum)

    @sumpf.Input(collections.Callable, ("_GetMaximumHarmonic", "_GetSamplingRate"))
    def SetMaximumHarmonic(self, max_harmonic):
        self._max_harmonic = max_harmonic
        self._nonlin_function.SetMaximumHarmonic(max_harmonic)

    @sumpf.Output(float)
    def _GetMaximumHarmonic(self):
        return self._nonlin_function.GetMaximumHarmonic()

    @sumpf.Output(float)
    def _GetSamplingRate(self):
        return self._prp.GetSamplingRate()*self._GetMaximumHarmonic()