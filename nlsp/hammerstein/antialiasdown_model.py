import sumpf
import nlsp
from .hammerstein_model import HammersteinModel

class AliasCompensatingHammersteinModelDownandUp(HammersteinModel):
    def __init__(self, input_signal=None,nonlin_func=nlsp.NonlinearFunction.power_series(degree=1),filter_impulseresponse=None,
                 upsampling_position=None):
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
        d = sumpf.modules.ResampleSignal(samplingrate=48000/self.branch)
        sumpf.connect(a.GetOutput,d.SetInput)
        super(AliasCompensatingHammersteinModelDownandUp,self).__init__(input_signal=d.GetOutput(),nonlin_func=self.nonlin_func,
                                                                      filter_impulseresponse=self.filter_inpulseresponse)
        # self.GetOutput = self.output_signal.GetSignal
        self.GetOutput = self.output_signal.GetOutput


    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.input_signal = signal

