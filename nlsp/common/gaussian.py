import sumpf
import numpy

class WhiteGaussianGenerator(object):
    def __init__(self, sampling_rate=48000.0, length=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, distribution=sumpf.modules.NoiseGenerator.GaussianDistribution()):
        self.__sampling_rate = float(sampling_rate)
        self.__length = float(length)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__distribution = distribution

    def SetLength(self,length):
        self.__length = float(length)

    def GetOutput(self):
        noise = sumpf.modules.NoiseGenerator(distribution=self.__distribution, samplingrate=self.__sampling_rate,
                                             length=self.__length).GetSignal()
        prop = sumpf.modules.ChannelDataProperties()
        prop.SetSignal(noise)
        bandpass = sumpf.modules.RectangleFilterGenerator(start_frequency=self.__start_frequency,
                                                                 stop_frequency=self.__stop_frequency,
                                                                 resolution=prop.GetResolution(),
                                                                 length=prop.GetSpectrumLength()).GetSpectrum()
        wgn = bandpass * sumpf.modules.FourierTransform(noise).GetSpectrum()
        return sumpf.modules.InverseFourierTransform(wgn).GetSignal()
        # wgn = numpy.random.normal(0.0,1.0,self.__length)
        # return sumpf.Signal(channels=(wgn,),samplingrate=self.__sampling_rate,labels=("wgn",))

    @sumpf.Output(float)
    def GetLength(self):
        return self.__length

    @sumpf.Output(float)
    def GetStartFrequency(self):
        return self.__start_frequency

    @sumpf.Output(float)
    def GetStopFrequency(self):
        return self.__stop_frequency


