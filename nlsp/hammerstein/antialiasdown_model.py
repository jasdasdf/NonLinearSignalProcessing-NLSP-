import sumpf
import nlsp
from .hammerstein_model import HammersteinModel

class AliasCompensatingHammersteinModelDownandUp(HammersteinModel):
    """
    A class to generate the output of the Aliasing compensated Hammerstein model.
    This extends the functionality of simple hammerstein model by upsampling the input signal to the Hammerstein model and the
    downsampling is done at different positions.
    It imports the sumpf modules to do the signal processing functions.
    """
    def __init__(self, input_signal=None, nonlin_func=nlsp.NonlinearFunction.power_series(degree=1),
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


        # create the signal processing objects
        self._asignal = sumpf.modules.AmplifySignal(input=input_signal)
        self._afilter = sumpf.modules.AmplifySignal(input=filter_impulseresponse)
        self._downsignal = sumpf.modules.ResampleSignal(samplingrate=self._asignal.GetOutput().GetSamplingRate() /
                                                                     nonlin_func.GetMaximumHarmonic(),
                                                        algorithm=self._resampling_algorithm)
        self._downfilter = sumpf.modules.ResampleSignal(samplingrate=self._asignal.GetOutput().GetSamplingRate() /
                                                                     nonlin_func.GetMaximumHarmonic(),
                                                        algorithm=self._resampling_algorithm)
        # define input and output methods
        self.SetInput = self._asignal.SetInput
        self.SetFilterIR = self._afilter.SetInput
        # self.SetNLFunction = self._nonlin_func.SetNonlinearFunction
        # self.SetMaximumHarmonic = self._nonlin_func.SetMaximumHarmonic

        # call the base classes constructor (which also calls _Connect)
        super(AliasCompensatingHammersteinModelDownandUp, self).__init__(input_signal=input_signal,
                                                                         nonlin_func=nonlin_func,
                                                                         filter_impulseresponse=filter_impulseresponse)
        self.GetOutput = self._itransform.GetSignal


    def _Connect(self):
        sumpf.connect(self._ampsignal.GetOutput, self._downsignal.SetInput)
        sumpf.connect(self._ampfilter.GetOutput, self._downfilter.SetInput)
        sumpf.connect(self._downsignal.GetOutput,self._nonlin_func.SetInput)
        sumpf.connect(self._nonlin_func.GetOutput,self._merger.AddInput)
        sumpf.connect(self._downfilter.GetOutput,self._merger.AddInput)
        sumpf.connect(self._merger.GetOutput,self._transform.SetSignal)
        sumpf.connect(self._transform.GetSpectrum,self._split1ch.SetInput)
        sumpf.connect(self._transform.GetSpectrum,self._split2ch.SetInput)
        sumpf.connect(self._split1ch.GetOutput,self._multiply.SetInput1)
        sumpf.connect(self._split2ch.GetOutput,self._multiply.SetInput2)
        sumpf.connect(self._multiply.GetOutput,self._itransform.SetSpectrum)
