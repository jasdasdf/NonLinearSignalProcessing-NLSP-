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
    def __init__(self, input_signal=None, nonlin_func=nlsp.NonlinearFunction.power_series(degree=1),
                 filter_impulseresponse=None, filterorder=20, filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=20),
                 attenuation=0.0001):
        """
        :param input_signal: the input signal instance to the Alias compensated Hammerstein model
        :param nonlin_func: the nonlinear function-instance for the nonlinear block
        :param filter_impulseresponse: the impulse response of the linear filter block
        :param filterorder: the order of the filter function used to lowpass the signal
        :param filterfunction: the type of filter used for lowpass operation. eg. BUTTERWORTH,CHEBYSHEV1,CHEBYSHEV2 etc
        :param attenuation: the attenuation of the cutoff frequency
        :return:
        """
        self._filterorder = filterorder
        self._filterfunction = filterfunction
        self._asignal = sumpf.modules.AmplifySignal(input=input_signal)
        self._afilter = sumpf.modules.AmplifySignal(input=filter_impulseresponse)
        self._cutofffreq = ((self._asignal.GetOutput().GetSamplingRate()/2)/nonlin_func.GetMaximumHarmonic())/\
                           (2**(20*math.log(attenuation,10)/(6*filterorder)))
        if input_signal is None:
            self._prp = sumpf.modules.ChannelDataProperties(signal_length=sumpf.Signal().GetDuration()*
                                                                          sumpf.Signal().GetSamplingRate(),
                                                            samplingrate=sumpf.Signal().GetSamplingRate())
        else:
            self._prp = sumpf.modules.ChannelDataProperties(signal_length=self._asignal.GetOutput().GetDuration()*
                                                                      self._asignal.GetOutput().GetSamplingRate(),
                                                  samplingrate=self._asignal.GetOutput().GetSamplingRate())
        self._resolution = self._prp.GetResolution()
        self._spectrallength = self._prp.GetSpectrumLength()
        self._lpfilter = sumpf.modules.FilterGenerator(filterfunction=self._filterfunction,frequency=self._cutofffreq,
                                               resolution=self._resolution,
                                          length=self._spectrallength)
        self._lptransform = sumpf.modules.FourierTransform()
        self._lpitransform = sumpf.modules.InverseFourierTransform()
        self._lpmultiply = sumpf.modules.MultiplySpectrums()

        # define input and output methods
        # self.SetNLFunction = self._nonlin_func.SetNonlinearFunction
        # self.SetMaximumHarmonic = self._nonlin_func.SetMaximumHarmonic
        self.SetInput = self._asignal.SetInput
        self.SetFilterIR = self._afilter.SetInput

        # call the base classes constructor (which also calls _Connect)
        super(AliasCompensatingHammersteinModelLowpass, self).__init__(input_signal=input_signal,
                                                                         nonlin_func=nonlin_func,
                                                                         filter_impulseresponse=filter_impulseresponse)
        self.GetOutput = self._itransform.GetSignal

    def _Connect(self):
        print self._ampsignal.GetOutput().GetDuration()*self._ampsignal.GetOutput().GetSamplingRate()
        sumpf.connect(self._lpfilter.GetSpectrum,self._lpmultiply.SetInput1)
        sumpf.connect(self._ampsignal.GetOutput, self._lptransform.SetSignal)
        sumpf.connect(self._lptransform.GetSpectrum, self._lpmultiply.SetInput2)
        # print self._lpfilter.GetSpectrum().GetResolution(),self._lptransform.GetSpectrum().GetResolution()
        # print self._lpfilter.GetSpectrum(),self._lptransform.GetSpectrum()
        # print self._lpmultiply.GetOutput()
        # self._lpitransform.SetSpectrum(self._lpmultiply.GetOutput())
        # print self._lpitransform.GetSignal()
        sumpf.connect(self._lpmultiply.GetOutput, self._lpitransform.SetSpectrum)
        sumpf.connect(self._lpitransform.GetSignal, self._nonlin_func.SetInput)
        sumpf.connect(self._nonlin_func.GetOutput, self._merger.AddInput)
        sumpf.connect(self._ampfilter.GetOutput, self._merger.AddInput)
        sumpf.connect(self._merger.GetOutput, self._transform.SetSignal)
        sumpf.connect(self._transform.GetSpectrum, self._split1ch.SetInput)
        sumpf.connect(self._transform.GetSpectrum, self._split2ch.SetInput)
        sumpf.connect(self._split1ch.GetOutput, self._multiply.SetInput1)
        sumpf.connect(self._split2ch.GetOutput, self._multiply.SetInput2)
        sumpf.connect(self._multiply.GetOutput, self._itransform.SetSpectrum)