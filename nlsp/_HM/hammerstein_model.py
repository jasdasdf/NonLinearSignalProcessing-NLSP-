import math
import sumpf
import nlsp
import common
import collections


class HammersteinModel(object):
    """
    A class to construct a Hammerstein model.
    The simple Hammerstein model consists of a nonlinear block followed by the linear filter block. The nonlinear block
    can be defined by power series or some other polynomial functions. It uses sumpf modules to do the signal processing
    stuff and function_factory functions to generate the nonlinear outputs. But also other functions like clipsignal,
    nonlinear clipping etc can also be used.
    """
    def __init__(self,input_signal=None, nonlin_func=nlsp.function_factory.power_series(1),filter_impulseresponse=None):
        """
        :param input_signal: the input signal
        :param nonlin_func: the nonlinear function
        :param filter_impulseresponse: the impulse response of the linear filter block
        """
        # interpret the input parameters
        if input_signal is None:
            input_signal = sumpf.Signal()
        if filter_impulseresponse is None:
            self._filterir = sumpf.modules.ImpulseGenerator(length=len(input_signal),
                                                            samplingrate=input_signal.GetSamplingRate()).GetSignal()
        else:
            self._filterir = filter_impulseresponse

        # set up the signal processing objects
        self._ampsignal = sumpf.modules.AmplifySignal(input=input_signal)
        self._nonlin_func = nlsp.NonlinearFunction(nonlin_func=nonlin_func)
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
        if nonlin_func is not None:
            self.SetNLFunction = self._nonlin_func.SetNonlinearFunction
            self.GetNLOutput = self._nonlin_func.GetOutput
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