import sumpf
import nlsp
from .hammerstein_model import HammersteinModel

class AliasCompensatingHammersteinModelLowpass(HammersteinModel):
    def __init__(self, input_signal=None, nonlin_func=nlsp.NonlinearFunction.power_series(degree=1), filter_impulseresponse=None, filterorder=20,
                 filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(), attenuation=0.0001):
        if input_signal is None:
            self.input_signal = sumpf.Signal()
        else:
            self.input_signal = input_signal
        self.nonlin_func = nonlin_func
        self.filter_inpulseresponse = filter_impulseresponse
        self.filterorder = filterorder
        self.filterfunction = filterfunction
        self.attenuation = attenuation
        self.prp = sumpf.modules.ChannelDataProperties(signal_length=self.input_signal.GetDuration()*self.input_signal.GetSamplingRate(),
                                                  samplingrate=self.input_signal.GetSamplingRate())
        self.branch = self.nonlin_func.GetMaximumHarmonic()
        f = sumpf.modules.FilterGenerator(filterfunction=self.filterfunction,frequency=20000/self.branch,resolution=self.prp.GetResolution(),
                                          length=self.prp.GetSpectrumLength())
        a = sumpf.modules.AmplifySignal(input=self.input_signal)
        t = sumpf.modules.FourierTransform()
        m = sumpf.modules.MultiplySpectrums(spectrum1=f.GetSpectrum())
        it = sumpf.modules.InverseFourierTransform()
        sumpf.connect(a.GetOutput,t.SetSignal)
        sumpf.connect(t.GetSpectrum,m.SetInput2)
        sumpf.connect(m.GetOutput,it.SetSpectrum)
        super(AliasCompensatingHammersteinModelLowpass,self).__init__(input_signal=it.GetSignal(),
                                                                      nonlin_func=self.nonlin_func,filter_impulseresponse=self.filter_inpulseresponse)
        # self.GetOutput = self.output_signal.GetSignal
        self.GetOutput = self.output_signal.GetOutput

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.input_signal = signal

