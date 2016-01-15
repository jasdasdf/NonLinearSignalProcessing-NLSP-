import math
import sumpf
import nlsp
import common
import collections

class HammersteinModel(object):
    """
    A class to generate the output of simple hammerstein model.
    The simple hammerstein model consists of a nonlinear block followed by the linear filter block. The nonlinear block
    can be defined by power series or some other polynomial functions.
    It uses sumpf modules to convolve, transform the signals and nonlinear function class to generate the nonlinear seq
    of the input signals.
    """
    def __init__(self,input_signal=None, nonlin_func=nlsp.NonlinearFunction.polynomials(1,"power"),
                 filter_impulseresponse=None):
        """
        :param input_signal: the input signal-instance to the Hammerstein model
        :param nonlin_func: the nonlinear function-instance for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :return:
        """
        # interpret the input parameters
        if input_signal is None:
            input_signal = sumpf.Signal()
        self._nonlin_func = nonlin_func
        if filter_impulseresponse is None:
            self._filterir = sumpf.modules.ImpulseGenerator(length=20).GetSignal()
        else:
            self._filterir = filter_impulseresponse

        # set up the signal processing objects
        self._ampsignal = sumpf.modules.AmplifySignal(input=input_signal)
        self._ampfilter = sumpf.modules.AmplifySignal(input=self._filterir)
        self._transform = sumpf.modules.FourierTransform()
        self._itransform = sumpf.modules.InverseFourierTransform()
        self._split1ch = sumpf.modules.SplitSpectrum(channels=[0])
        self._split2ch = sumpf.modules.SplitSpectrum(channels=[1])
        self._merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        self._multiply = sumpf.modules.MultiplySpectrums()

        # define input and output methods
        self.SetInput = self._ampsignal.SetInput
        self.SetFilterIR = self._ampfilter.SetInput
        if self._nonlin_func is  not None:
            self.SetNLFunction = self._nonlin_func.SetNonlinearFunction
            self.SetMaximumHarmonic = self._nonlin_func.SetMaximumHarmonic
        self.GetOutput = self._itransform.GetSignal

        # connect the signal processing objects
        self._Connect()

    def _Connect(self):
        sumpf.connect(self._ampsignal.GetOutput,self._nonlin_func.SetInput)
        sumpf.connect(self._nonlin_func.GetOutput,self._merger.AddInput)
        sumpf.connect(self._ampfilter.GetOutput,self._merger.AddInput)
        sumpf.connect(self._merger.GetOutput,self._transform.SetSignal)
        sumpf.connect(self._transform.GetSpectrum,self._split1ch.SetInput)
        sumpf.connect(self._transform.GetSpectrum,self._split2ch.SetInput)
        sumpf.connect(self._split1ch.GetOutput,self._multiply.SetInput1)
        sumpf.connect(self._split2ch.GetOutput,self._multiply.SetInput2)
        sumpf.connect(self._multiply.GetOutput,self._itransform.SetSpectrum)


    # @sumpf.Input(collections.Callable, "_Connect")
    # def SetNLFunction(self,nonlinear_function):
    #     self._nonlin_func = nonlinear_function

# class Logger(object):
#     def __init__(self, name):
#         self.__name = name
#
#     @sumpf.Trigger()
#     def log(self):
#         print "LOG", self.__name
#
# lg = Logger(name="amp")
# lg._Logger__value = 9
# sumpf.connect(self.amp.GetOutput, lg.log)

# class NewLogger(Logger):
#     def __init(self):
#         Logger.__init__(self, name="")
#         self.value = 12