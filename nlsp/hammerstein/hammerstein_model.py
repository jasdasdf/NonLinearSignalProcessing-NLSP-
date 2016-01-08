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
    def __init__(self,input_signal=None,nonlin_func=nlsp.NonlinearFunction.power_series(1),filter_impulseresponse=None):
        """
        :param input_signal: the input signal-instance to the Hammerstein model
        :param nonlin_func: the nonlinear function-instance for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :return:
        """
        self.input = input_signal
        self.inputstage = sumpf.modules.AmplifySignal()
        self.inputstage.SetInput(self.input)
        self.nonlin_func = nonlin_func
        if filter_impulseresponse is None:
            self.__filterir = sumpf.Signal()
        else:
            self.__filterir = filter_impulseresponse
        a = sumpf.modules.AmplifySignal(input=self.__filterir)
        t = sumpf.modules.FourierTransform()
        it = sumpf.modules.InverseFourierTransform()
        s1 = sumpf.modules.SplitSpectrum(channels=[0])
        s2 = sumpf.modules.SplitSpectrum(channels=[1])
        m = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        f = sumpf.modules.MultiplySpectrums()
        # sumpf.connect(self.inputstage.GetOutput,self.nonlin_func.SetInput)
        # sumpf.connect(self.nonlin_func.GetOutput,m.AddInput)
        # sumpf.connect(a.GetOutput,m.AddInput)
        # sumpf.connect(m.GetOutput,t.SetSignal)
        # sumpf.connect(t.GetSpectrum,s1.SetInput)
        # sumpf.connect(t.GetSpectrum,s2.SetInput)
        # sumpf.connect(s1.GetOutput,f.SetInput1)
        # sumpf.connect(s2.GetOutput,f.SetInput2)
        # sumpf.connect(f.GetOutput,it.SetSpectrum)
        # self.output_signal = it
        # self.GetOutput = self.output_signal.GetSignal
        # self.GetNLOutput = self.nonlin_func.GetOutput

        c = sumpf.modules.ConvolveSignals()
        sumpf.connect(self.inputstage.GetOutput,self.nonlin_func.SetInput)
        sumpf.connect(a.GetOutput,c.SetInput1)
        sumpf.connect(self.nonlin_func.GetOutput,c.SetInput2)
        self.output_signal = c
        self.GetOutput = self.output_signal.GetOutput
        self.GetNLOutput = self.nonlin_func.GetOutput
        # print len(c.GetOutput())


    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.input = signal

    # def _Connect(self):
    #     # connect the input to the nonlinear function, the nonlinear function to
    #     # the filter and the filter to the output
    #     # connect the input: self.SetInput = self._nonlin_func.SetInput

#
# class AliasCompensatingHammersteinModel(HammersteinModel):
#     def __init__(self, input_signal=None, nonlinear_function=None, filter_impulseresponse=None, branch=None, up_position=None):
#         HammersteinModel.__init__(self,input_signal=input_signal,nonlinear_function=nonlinear_function,filter_impulseresponse=filter_impulseresponse,branch=branch)
#
#

#
