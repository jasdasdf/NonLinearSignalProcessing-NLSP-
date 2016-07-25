import sumpf
import numpy

class WhiteGaussianGenerator(object):
    def __init__(self, sampling_rate=48000.0, length=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(),factor=1.0):
        self.__sampling_rate = float(sampling_rate)
        self.__length = float(length)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__distribution = distribution
        self.__excitation_factor = factor
        self._generate()

    def _generate(self):
        noise = sumpf.modules.NoiseGenerator(distribution=self.__distribution, samplingrate=self.__sampling_rate,
                                             length=self.__length).GetSignal()
        prop = sumpf.modules.ChannelDataProperties()
        prop.SetSignal(noise)
        bandpass = sumpf.modules.RectangleFilterGenerator(start_frequency=self.__start_frequency,
                                                                 stop_frequency=self.__stop_frequency,
                                                                 resolution=prop.GetResolution(),
                                                                 length=prop.GetSpectrumLength()).GetSpectrum()
        wgn = bandpass * sumpf.modules.FourierTransform(noise).GetSpectrum()
        self.__output = sumpf.modules.InverseFourierTransform(wgn).GetSignal()
        # wgn = numpy.random.normal(0.0,1.0,self.__length)
        # return sumpf.Signal(channels=(wgn,),samplingrate=self.__sampling_rate,labels=("wgn",))

    @sumpf.Input(int,"GetOutput")
    def SetLength(self,length):
        self.__length = float(length)
        self._generate()

    @sumpf.Output(float)
    def GetLength(self):
        return self.__length

    @sumpf.Output(float)
    def GetStartFrequency(self):
        return self.__start_frequency

    @sumpf.Output(float)
    def GetStopFrequency(self):
        return self.__stop_frequency

    @sumpf.Output(float)
    def GetFactor(self):
        return self.__excitation_factor

    @sumpf.Input(float,["GetFactor", "GetOutput"])
    def SetFactor(self,factor=1.0):
        self.__excitation_factor = factor

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        return sumpf.modules.AmplifySignal(input=self.__output,factor=self.GetFactor()).GetOutput()

