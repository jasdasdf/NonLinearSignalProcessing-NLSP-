import numpy
import sumpf
import nlsp
import math

class WindowedSweepGenerator(object):
    def __init__(self, sampling_rate=48000.0, length=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, silence_duration=0.03, fade_out=0.02, fade_in=0.02,
                 function=sumpf.modules.SweepGenerator.Exponential):
        self.__sampling_rate = float(sampling_rate)
        self.__length = float(length)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__silence_duration = float(silence_duration)
        self.__fade_out = float(fade_out)
        self.__fade_in = float(fade_in)
        self.__function = function

    def SetLength(self,length):
        self.__length = float(length)

    def GetOutput(self):
        # get lengths from durations
        if self.__silence_duration != 0.0:
            d2l = sumpf.modules.DurationToLength(duration=self.__fade_out, samplingrate=self.__sampling_rate)
            fade_out_length = d2l.GetLength()
            d2l.SetDuration(duration=self.__fade_in)
            fade_in_length = d2l.GetLength()
            d2l.SetDuration(self.__silence_duration)
            silence_length = d2l.GetLength()
            sumpf.destroy_connectors(d2l)
            sweep_length = self.__length - silence_length
            # get signals
            slg = sumpf.modules.SilenceGenerator(samplingrate=self.__sampling_rate, length=silence_length)
            silence = slg.GetSignal()
            sumpf.destroy_connectors(slg)
            if (fade_out_length == 0.0 and fade_in_length ==0.0):
                interval = None
            else:
                interval = (fade_in_length, -fade_out_length)
            swg = sumpf.modules.SweepGenerator(start_frequency=self.__start_frequency,
                                               stop_frequency=self.__stop_frequency,
                                               function=self.__function,
                                               interval=interval,
                                               samplingrate=self.__sampling_rate,
                                               length=sweep_length)
            sweep = swg.GetSignal()
            sumpf.destroy_connectors(swg)
            if fade_in_length == 0.0:
                raise_interval = None
            else:
                raise_interval = (0,fade_in_length)
            wng = sumpf.modules.WindowGenerator(raise_interval= raise_interval,
                                                fall_interval=(-fade_out_length, -1),
                                                function=sumpf.modules.WindowGenerator.Hanning(),
                                                samplingrate=self.__sampling_rate,
                                                length=sweep_length)
            window = wng.GetSignal()
            sumpf.destroy_connectors(wng)
            # combine signals
            windowed_sweep = sweep * window
            cat = sumpf.modules.ConcatenateSignals(signal1=windowed_sweep, signal2=silence)
            concatenated_sweep = cat.GetOutput()
            sumpf.destroy_connectors(cat)
        else:
            print "normal sweep"
            concatenated_sweep = sumpf.modules.SweepGenerator(self.__start_frequency,self.__stop_frequency,
                                                              samplingrate=self.__sampling_rate,
                                                              length=self.__length,function=self.__function).GetSignal()
        self.__sweep_signal = sumpf.modules.AmplifySignal(concatenated_sweep)
        return self.__sweep_signal.GetOutput()

    @sumpf.Output(float)
    def GetLength(self):
        sweep_duration = (self.__length/self.__sampling_rate) - self.__fade_out - self.__silence_duration - self.__fade_in
        return sweep_duration*self.__sampling_rate

    @sumpf.Output(float)
    def GetStartFrequency(self):
        return self.__start_frequency

    @sumpf.Output(float)
    def GetStopFrequency(self):
        return self.__stop_frequency


class NovakSweepGenerator_Sine(object):
    def __init__(self, sampling_rate=48000.0, length=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, fade_out=0.02, fade_in=0.02):

        self.__sampling_rate = float(sampling_rate)
        self.__approx_length = float(length)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__fade_out = float(fade_out*self.__sampling_rate)
        self.__fade_in = float(fade_in*self.__sampling_rate)

    @sumpf.Input(float,"GetLength")
    def SetLength(self,length):
        self.__approx_length = float(length)

    def GetOutput(self):
        t = numpy.arange(0,self.GetLength()/self.__sampling_rate,1/self.__sampling_rate)
        s = numpy.sin(2*numpy.pi*self.__start_frequency*self.GetSweepParameter()*(numpy.exp(t/self.GetSweepParameter())-1))
        if self.__fade_in > 0:
            s[0:self.__fade_in] = s[0:self.__fade_in] * ((-numpy.cos(numpy.arange(self.__fade_in)/self.__fade_in*math.pi)+1) / 2)
        if self.__fade_out > 0:
            s[-self.__fade_out:] = s[-self.__fade_out:] *  ((numpy.cos(numpy.arange(self.__fade_out)/self.__fade_out*numpy.pi)+1) / 2)
        signal = sumpf.Signal(channels=(s,),samplingrate=self.__sampling_rate,labels=("Sweep signal",))
        if len(signal) % 2 != 0:
            signal = sumpf.modules.CutSignal(signal,start=0,stop=-1).GetOutput()
        return signal

    def GetReversedOutput(self, length=None):
        if length is None:
            length = self.GetLength()
        sampling_rate = self.GetOutput().GetSamplingRate()
        sweep_parameter = self.GetSweepParameter()
        # fft_len = int(2**numpy.ceil(numpy.log2(length)))
        fft_len = int(length)
        interval = numpy.linspace(0, sampling_rate/2, num=fft_len/2+1)
        inverse_sweep = 2*numpy.sqrt(interval/sweep_parameter)*numpy.exp(1j*(2*numpy.pi*sweep_parameter*interval*(self.GetStartFrequency()/interval +
                                                                     numpy.log(interval/self.GetStartFrequency()) - 1) + numpy.pi/4))
        inverse_sweep[0] = 0j
        rev_sweep = numpy.fft.irfft(inverse_sweep)
        rev_sweep = sumpf.Signal(channels=(rev_sweep,),samplingrate=sampling_rate,labels=("Reversed Sweep signal",))
        return rev_sweep

    def GetSweepParameter(self):
        L = 1/self.__start_frequency * round((self.__approx_length/self.__sampling_rate)*
                                             self.__start_frequency/numpy.log(self.__stop_frequency/self.__start_frequency))
        return L

    @sumpf.Output(float)
    def GetLength(self):
        T_hat = self.GetSweepParameter()*numpy.log(self.__stop_frequency/self.__start_frequency)
        length = round(self.__sampling_rate*T_hat-1)
        return length

    @sumpf.Output(float)
    def GetStartFrequency(self):
        return self.__start_frequency

    @sumpf.Output(float)
    def GetStopFrequency(self):
        return self.__stop_frequency

class NovakSweepGenerator_Cosine(object):
    def __init__(self, sampling_rate=48000.0, length=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, fade_out=0.02, fade_in=0.02):

        self.__sampling_rate = float(sampling_rate)
        self.__approx_length = float(length)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__fade_out = float(fade_out*self.__sampling_rate)
        self.__fade_in = float(fade_in*self.__sampling_rate)

    @sumpf.Input(float,"GetLength")
    def SetLength(self,length):
        self.__approx_length = float(length)

    def GetOutput(self):
        t = numpy.arange(0,self.GetLength()/self.__sampling_rate,1/self.__sampling_rate)
        s = numpy.cos(2*numpy.pi*self.__start_frequency*self.GetSweepParameter()*(numpy.exp(t/self.GetSweepParameter())-1))
        if self.__fade_in > 0:
            s[0:self.__fade_in] = s[0:self.__fade_in] * ((-numpy.cos(numpy.arange(self.__fade_in)/self.__fade_in*math.pi)+1) / 2)
        if self.__fade_out > 0:
            s[-self.__fade_out:] = s[-self.__fade_out:] *  ((numpy.cos(numpy.arange(self.__fade_out)/self.__fade_out*numpy.pi)+1) / 2)
        signal = sumpf.Signal(channels=(s,),samplingrate=self.__sampling_rate,labels=("Sweep signal",))
        if len(signal) % 2 != 0:
            signal = sumpf.modules.CutSignal(signal,start=0,stop=-1).GetOutput()
        return signal

    def GetReversedOutput(self, length=None):
        if length is None:
            length = self.GetLength()
        sampling_rate = self.GetOutput().GetSamplingRate()
        sweep_parameter = self.GetSweepParameter()
        # fft_len = int(2**numpy.ceil(numpy.log2(length)))
        fft_len = int(length)
        interval = numpy.linspace(0, sampling_rate/2, num=fft_len/2+1)
        inverse_sweep = 2*numpy.sqrt(interval/sweep_parameter)*numpy.exp(1j*(2*numpy.pi*sweep_parameter*interval*(self.GetStartFrequency()/interval +
                                                                     numpy.log(interval/self.GetStartFrequency()) - 1) + numpy.pi/4))
        inverse_sweep[0] = 0j
        rev_sweep = numpy.fft.irfft(inverse_sweep)
        rev_sweep = sumpf.Signal(channels=(rev_sweep,),samplingrate=sampling_rate,labels=("Reversed Sweep signal",))
        return rev_sweep

    def GetSweepParameter(self):
        L = 1/self.__start_frequency * round((self.__approx_length/self.__sampling_rate)*
                                             self.__start_frequency/numpy.log(self.__stop_frequency/self.__start_frequency))
        return L

    @sumpf.Output(float)
    def GetLength(self):
        T_hat = self.GetSweepParameter()*numpy.log(self.__stop_frequency/self.__start_frequency)
        length = round(self.__sampling_rate*T_hat-1)
        return length

    @sumpf.Output(float)
    def GetStartFrequency(self):
        return self.__start_frequency

    @sumpf.Output(float)
    def GetStopFrequency(self):
        return self.__stop_frequency
