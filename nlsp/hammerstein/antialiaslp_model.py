#
# class AliasCompensatingHammersteinModelLowpass(AliasCompensatingHammersteinModel):
#     def __init__(self, input_signal=None, nonlinear_function=None, filter_impulseresponse=None, filterorder=None, filterfunction=None, attenuation=0.0001):
#         self.__inputsignal = input_signal
#         if filterorder is None:
#             self.__filterorder = 20
#         else:
#             self.__filterorder = filterorder
#         if filterfunction is None:
#             self.__filterfunction = sumpf.modules.FilterGenerator.BUTTERWORTH(order=self.__filterorder)
#         else:
#             self.__filterfunction = filterfunction
#         self.__filterir = filter_impulseresponse
#         self.__nonlinearfunc = nonlinear_function
#         prp = sumpf.modules.ChannelDataProperties(signal_length=self.__inputsignal.GetDuration()*self.__inputsignal.GetSamplingRate(),samplingrate=self.__inputsignal.GetSamplingRate())
#         filt = sumpf.modules.FilterGenerator(filterfunction=self.__filterfunction,frequency=20000/self._branch,resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
#         t = sumpf.modules.FourierTransform()
#         it = sumpf.modules.InverseFourierTransform()
#         m = sumpf.modules.MultiplySpectrums(spectrum2=filt)
#         a = sumpf.modules.AmplifySignal(input=self.__inputsignal,factor=1.0)
#         sumpf.connect(a.GetOutput,t.SetSignal)
#         sumpf.connect(t.GetSpectrum,m.SetInput1)
#         sumpf.connect(m.GetOutput,it.SetSpectrum)
#         self.__lpsignal = it.GetSignal()
#         AliasCompensatingHammersteinModel.__init__(self,input_signal=self.__lpsignal,nonlinear_function=self.__nonlinearfunc,filter_impulseresponse=self.__filterir,branch=self._branch,up_position=0)
#
#     def _Connect(self):
#         # connect the input to the lowpass, the lowpass to the nonlinear function etc.
