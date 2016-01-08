import sumpf
import nlsp
from .hammerstein_model import HammersteinModel

class AliasCompensatingHammersteinModelDownandUp(HammersteinModel):
    """
    A class to generate the output of the Aliasing compensated Hammerstein model.
    This extends the functionality of simple hammerstein model by downsampling the input signal to the Hammerstein model and the
    upsampling is done at different positions.
    It imports the sumpf modules to do the signal processing functions.
    """
    def __init__(self, input_signal=None,nonlin_func=nlsp.NonlinearFunction.power_series(degree=1),filter_impulseresponse=None,
                 upsampling_position=None):
        """
        :param input_signal: the input signal instance to the Alias compensated Hammerstein model
        :param nonlin_func: the nonlinear function-instance for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :param upsampling_position: the upsampling position, It is a integer value which may be 1,2,3 for upsampling after nonlinear
                                    signal block, after the linear filter block, after the summation of the hammerstein model signals
                                    respectively. It this parameter is not given then the upsampling is done at the end
        :return:
        """
        if input_signal is None:
            self.input_signal = sumpf.Signal()
        else:
            self.input_signal = input_signal
        self.nonlin_func = nonlin_func
        self.filter_inpulseresponse = filter_impulseresponse
        self.prp = sumpf.modules.ChannelDataProperties(signal_length=self.input_signal.GetDuration()*self.input_signal.GetSamplingRate(),
                                                  samplingrate=self.input_signal.GetSamplingRate())
        self.branch = self.nonlin_func.GetMaximumHarmonic()
        a = sumpf.modules.AmplifySignal(input=self.input_signal)
        d = sumpf.modules.ResampleSignal(samplingrate=self.input_signal.GetSamplingRate()/self.branch)
        sumpf.connect(a.GetOutput,d.SetInput)
        super(AliasCompensatingHammersteinModelDownandUp,self).__init__(input_signal=d.GetOutput(),nonlin_func=self.nonlin_func,
                                                                      filter_impulseresponse=self.filter_inpulseresponse)
        # self.GetOutput = self.output_signal.GetSignal
        self.GetOutput = self.output_signal.GetOutput


    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.input_signal = signal

