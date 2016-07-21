import sumpf
import nlsp
from .hammerstein_model import HammersteinModel
import collections
import math

class AliasingCompensatedHM_upsampling(HammersteinModel):
    """
    This class is derived from HammersteinModel class. This compensates the aliasing problem of the HammersteinModel.
    In this aliasing compensated Hammerstein model, an upsampler is used to compensate the aliasing. The upsampled
    signal is downsampled again to the original sampling rate. The upsampling rate is chosen based on the degree of the
    polynomials used.
    It uses sumpf modules to do the signal processing stuff.
    """
    def __init__(self, input_signal=None, nonlin_func=nlsp.function_factory.power_series(1), max_harm=1,
                 filter_impulseresponse=None,
                 resampling_algorithm=sumpf.modules.ResampleSignal.SPECTRUM,
                 downsampling_position=2):
        """
        :param input_signal: the input signal
        :param nonlin_func: the nonlinear function
        :param filter_impulseresponse: the impulse response of the linear filter block
        :param resampling_algorithm: the algorithm which can be used to downsample and upsample the signal
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
        self._downsampling_position = downsampling_position
        self._downnloutput = sumpf.modules.ResampleSignal(algorithm=self._resampling_algorithm)
        self._downoutput2 = sumpf.modules.ResampleSignal(algorithm=self._resampling_algorithm)

        self.SetNLFunction = self._nonlin_function.SetNonlinearFunction

        # call the base classes constructor (which also calls _Connect)
        super(AliasingCompensatedHM_upsampling, self).__init__(input_signal=input_signal,
                                                                         nonlin_func=None,
                                                                         filter_impulseresponse=filter_impulseresponse)
        if self._downsampling_position == 1:
            self.GetOutput = self._downoutput.GetOutput
        else:
            self.GetOutput = self._itransform.GetSignal
        self.GetMaximumHarmonic = self._GetMaximumHarmonic

    def _Connect(self):
        sumpf.connect(self._ampsignal.GetOutput, self._prp.SetSignal)
        sumpf.connect(self._GetSamplingRateSignal, self._upsignal.SetSamplingRate)
        sumpf.connect(self._GetSamplingRateFilter, self._upfilter.SetSamplingRate)
        sumpf.connect(self._Getattenuation, self._attenuator.SetAmplificationFactor)
        sumpf.connect(self._ampsignal.GetOutput, self._upsignal.SetInput)
        sumpf.connect(self._ampfilter.GetOutput, self._upfilter.SetInput)
        sumpf.connect(self._upsignal.GetOutput,self._nonlin_function.SetInput)
        sumpf.connect(self._nonlin_function.GetOutput, self._attenuator.SetInput)
        sumpf.connect(self._GetSamplingRateFilter, self._downoutput2.SetSamplingRate)
        sumpf.connect(self._attenuator.GetOutput, self._downoutput2.SetInput)
        sumpf.connect(self._downoutput2.GetOutput, self._merger.AddInput)
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
    def _GetSamplingRateFilter(self):
        if self._downsampling_position == 1:
            # temp = self._prp.GetSamplingRate() * self._GetMaximumHarmonic() # Full resampling
            temp = self._prp.GetSamplingRate()*math.ceil((self._GetMaximumHarmonic()+1.0)/2.0) # Reduced resampling
        elif self._downsampling_position == 2:
            temp = self._prp.GetSamplingRate()
        return temp

    @sumpf.Output(float)
    def _GetSamplingRateSignal(self):
        # temp = self._prp.GetSamplingRate() * self._GetMaximumHarmonic() # Full resampling
        temp = self._prp.GetSamplingRate()*math.ceil((self._GetMaximumHarmonic()+1.0)/2.0) # Reduced resampling
        return temp

    @sumpf.Output(float)
    def _Getattenuation(self):
        return self._prp.GetSamplingRate()/self._GetSamplingRateFilter()
        # return (1/float(self._GetMaximumHarmonic()))

    @sumpf.Output(sumpf.Signal)
    def GetNLOutput(self):
        """
        Gets the output of the nonlinear block of the Hammerstein model. The output of the nonlinear block is downsampled
        to the original sampling rate.
        :return: the output of the nonlinear block of the Hammerstein model
        """
        sumpf.connect(self._nonlin_function.GetOutput,self._downnloutput.SetInput)
        sumpf.connect(self._prp.GetSamplingRate, self._downnloutput.SetSamplingRate)
        return self._downnloutput.GetOutput()