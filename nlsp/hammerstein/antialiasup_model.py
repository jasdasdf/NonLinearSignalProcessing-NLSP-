import sumpf
import nlsp
from .hammerstein_model import HammersteinModel

class AliasCompensatingHammersteinModelUpandDown(HammersteinModel):
    """
    A class to generate the output of the Aliasing compensated Hammerstein model.
    This extends the functionality of simple hammerstein model by upsampling the input signal to the Hammerstein model and the
    downsampling is done at different positions.
    It imports the sumpf modules to do the signal processing functions.
    """
    def __init__(self, input_signal=None,nonlin_func=nlsp.NonlinearFunction.power_series(degree=1),filter_impulseresponse=None,
                 downsampling_position=None,resampling_algorithm = sumpf.modules.ResampleSignal.SPECTRUM):
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
        if input_signal is None:
            self.input_signal = sumpf.Signal()
        else:
            self.input_signal = input_signal
        self.nonlin_func = nonlin_func
        self.branch = self.nonlin_func.GetMaximumHarmonic()
        if filter_impulseresponse is None:
            self.filter_inpulseresponse = sumpf.modules.ImpulseGenerator(length=2,
                                                                         samplingrate=self.input_signal.GetSamplingRate()).GetSignal()
        else:
            self.filter_inpulseresponse = filter_impulseresponse
        self.resampling_algorithm = resampling_algorithm
        self.prp = sumpf.modules.ChannelDataProperties(signal_length=self.input_signal.GetDuration()*self.input_signal.GetSamplingRate(),
                                                  samplingrate=self.input_signal.GetSamplingRate())
        self.ai = sumpf.modules.AmplifySignal(input=self.input_signal)
        self.af = sumpf.modules.AmplifySignal(input=self.filter_inpulseresponse)
        self.sig_samprate = self.ai.GetOutput().GetSamplingRate()
        self.di = sumpf.modules.ResampleSignal(samplingrate=self.sig_samprate*self.branch,algorithm=self.resampling_algorithm)
        self.df = sumpf.modules.ResampleSignal(samplingrate=self.sig_samprate*self.branch,algorithm=self.resampling_algorithm)
        sumpf.connect(self.ai.GetOutput,self.di.SetInput)
        sumpf.connect(self.af.GetOutput,self.df.SetInput)
        super(AliasCompensatingHammersteinModelUpandDown,self).__init__(input_signal=self.di.GetOutput(),nonlin_func=self.nonlin_func,
                                                                      filter_impulseresponse=self.df.GetOutput())
        self.SetInput = self.ai.SetInput
        self.SetFilterIR = self.af.SetInput
        self.GetOutput = self.it.GetSignal
        self.GetNLOutput = self.nonlin_func.GetOutput
