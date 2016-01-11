import sumpf
import nlsp
import common

class HammersteinModel(object):
    """
    A class to generate the output of simple hammerstein model.
    The simple hammerstein model consists of a nonlinear block followed by the linear filter block. The nonlinear block can be defined by power
    series or some other polynomial functions.
    It uses sumpf modules to convolve, transform the signals and nonlinear function class to generate the nonlinear seq of the input signals.
    """
    def __init__(self,input_signal=None,nonlin_func=nlsp.NonlinearFunction.power_series(1),
                 filter_impulseresponse=None):
        """
        :param input_signal: the input signal-instance to the Hammerstein model
        :param nonlin_func: the nonlinear function-instance for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :return:
        """
        if input_signal is None:
            self.input = sumpf.Signal()
        else:
            self.input = input_signal
        self.nonlin_func = nonlin_func
        if filter_impulseresponse is None:
            self.filterir = sumpf.modules.ImpulseGenerator(length=2).GetSignal()
        else:
            self.filterir = filter_impulseresponse
        self.inputstage = sumpf.modules.AmplifySignal()
        self.inputstage.SetInput(self.input)
        self.af = sumpf.modules.AmplifySignal(input=self.filterir)
        print self.inputstage.GetOutput().GetSamplingRate(),self.af.GetOutput().GetSamplingRate()
        self.t = sumpf.modules.FourierTransform()
        self.it = sumpf.modules.InverseFourierTransform()
        self.s1 = sumpf.modules.SplitSpectrum(channels=[0])
        self.s2 = sumpf.modules.SplitSpectrum(channels=[1])
        self.m = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        self.f = sumpf.modules.MultiplySpectrums()
        sumpf.connect(self.inputstage.GetOutput,self.nonlin_func.SetInput)
        sumpf.connect(self.nonlin_func.GetOutput,self.m.AddInput)
        sumpf.connect(self.af.GetOutput,self.m.AddInput)
        sumpf.connect(self.m.GetOutput,self.t.SetSignal)
        sumpf.connect(self.t.GetSpectrum,self.s1.SetInput)
        sumpf.connect(self.t.GetSpectrum,self.s2.SetInput)
        sumpf.connect(self.s1.GetOutput,self.f.SetInput1)
        sumpf.connect(self.s2.GetOutput,self.f.SetInput2)
        sumpf.connect(self.f.GetOutput,self.it.SetSpectrum)
        self.SetInput = self.inputstage.SetInput
        self.SetFilterIR = self.af.SetInput
        self.GetOutput = self.it.GetSignal
        self.GetNLOutput = self.nonlin_func.GetOutput


