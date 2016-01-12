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
    def __init__(self,input_signal=None,nonlin_func=nlsp.NonlinearFunction.power_series(degree=1),filter_impulseresponse=None,filterorder=20,
                 filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(),attenuation=0.0001):
        """
        :param input_signal: the input signal instance to the Alias compensated Hammerstein model
        :param nonlin_func: the nonlinear function-instance for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :param filterorder: the order of the filter function used to lowpass the signal
        :param filterfunction: the type of filter used for lowpass operation. eg. BUTTERWORTH,CHEBYSHEV1,CHEBYSHEV2 etc
        :param attenuation: the attenuation of the cutoff frequency
        :return:
        """
        if input_signal is None:
            self.input_signal = sumpf.Signal()
        else:
            self.input_signal = input_signal
        self.a = sumpf.modules.AmplifySignal(input=self.input_signal)
        self.nonlin_func = nonlin_func
        if filter_impulseresponse is None:
            self.filter_inpulseresponse = sumpf.modules.ImpulseGenerator(length=2).GetSignal()
        else:
            self.filter_inpulseresponse = filter_impulseresponse
        self.branch = self.nonlin_func.GetMaximumHarmonic()
        self.filterorder = filterorder
        self.filterfunction = filterfunction
        self.attenuation = 20*math.log(attenuation,10)
        self.cutofffreq = (24000/self.branch)/(2**(self.attenuation/(6*self.filterorder)))
        self.prp = sumpf.modules.ChannelDataProperties(signal_length=self.input_signal.GetDuration()*self.input_signal.GetSamplingRate(),
                                                  samplingrate=self.input_signal.GetSamplingRate())
        self.f = sumpf.modules.FilterGenerator(filterfunction=self.filterfunction,frequency=self.cutofffreq,resolution=self.prp.GetResolution(),
                                          length=self.prp.GetSpectrumLength())
        self.t = sumpf.modules.FourierTransform()
        self.m = sumpf.modules.MultiplySpectrums(spectrum1=self.f.GetSpectrum())
        self.it = sumpf.modules.InverseFourierTransform()
        sumpf.connect(self.a.GetOutput,self.t.SetSignal)
        sumpf.connect(self.t.GetSpectrum,self.m.SetInput2)
        sumpf.connect(self.m.GetOutput,self.it.SetSpectrum)
        super(AliasCompensatingHammersteinModelLowpass,self).__init__(input_signal=self.it.GetSignal(),
                                                                      nonlin_func=self.nonlin_func,filter_impulseresponse=self.filter_inpulseresponse)
        self.SetInput = self.a.SetInput
        self.GetOutput = self.it.GetSignal
        self.GetNLOutput = self.nonlin_func.GetOutput