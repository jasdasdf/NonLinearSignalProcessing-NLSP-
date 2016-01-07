import sumpf
import nlsp
import common

class HammersteinModel(object):
    def __init__(self,input_signal=None,nonlin_func=nlsp.NonlinearFunction.power_series(1),filter_impulseresponse=None):
        self.__input = input_signal
        self.__inputstage = sumpf.modules.AmplifySignal()
        self.__inputstage.SetInput(self.__input)
        self.__nonlin_func = nonlin_func
        self.__filterir = filter_impulseresponse
        a = sumpf.modules.AmplifySignal(input=self.__filterir)
        t = sumpf.modules.FourierTransform()
        it = sumpf.modules.InverseFourierTransform()
        s1 = sumpf.modules.SplitSpectrum(channels=[0])
        s2 = sumpf.modules.SplitSpectrum(channels=[1])
        m = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        f = sumpf.modules.MultiplySpectrums()
        sumpf.connect(self.__inputstage.GetOutput,self.__nonlin_func.SetInput)
        sumpf.connect(self.__nonlin_func.GetOutput,m.AddInput)
        sumpf.connect(a.GetOutput,m.AddInput)
        sumpf.connect(m.GetOutput,t.SetSignal)
        sumpf.connect(t.GetSpectrum,s1.SetInput)
        sumpf.connect(t.GetSpectrum,s2.SetInput)
        sumpf.connect(s1.GetOutput,f.SetInput1)
        sumpf.connect(s2.GetOutput,f.SetInput2)
        sumpf.connect(f.GetOutput,it.SetSpectrum)
        self.__output_signal = it
        self.GetOutput = self.__output_signal.GetSignal
        self.GetNLOutput = self.__nonlin_func.GetOutput

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.__input = signal



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
