#
# class AliasCompensatingHammersteinModelUpsample(AliasCompensatingHammersteinModel):
#     def __init__(self,input_signal=None, nonlinear_function=None, filter_impulseresponse=None, up_position=None):
#         self.__inputsignal = input_signal
#         self.__nonlinearfunc = nonlinear_function
#         self.__filterir = filter_impulseresponse
#         self.__uppos = up_position
#         prp = sumpf.modules.ChannelDataProperties(signal_length=self.__inputsignal.GetDuration()*self.__inputsignal.GetSamplingRate(),samplingrate=self.__inputsignal.GetSamplingRate())
#         filt = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=20),frequency=20000/self._branch,resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
#         ds = sumpf.modules.ResampleSignal(samplingrate=self.__inputsignal.GetSamplingRate()/self._branch)
#         t = sumpf.modules.FourierTransform()
#         m = sumpf.modules.MultiplySpectrums(spectrum2=filt)
#         it = sumpf.modules.InverseFourierTransform()
#         a = sumpf.modules.AmplifySignal(input=input_signal,factor=1.0)
#         sumpf.connect(a.GetOutput, t.SetSignal)
#         sumpf.connect(t.GetSpectrum, m.SetInput1)
#         sumpf.connect(m.GetOutput, it.SetSpectrum)
#         sumpf.connect(it.GetSignal, ds.SetInput)
#         self.__dssignal = ds.GetOutput()
#         AliasCompensatingHammersteinModel.__init__(self,input_signal=self.__dssignal,nonlinear_function=self.__nonlinearfunc,filter_impulseresponse=self.__filterir,branch=self._branch,up_position=self.__uppos)
#
#
