import numpy
import sumpf
import math
import common.plot as plot

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

    def GetProperties(self):
        sweep_duration = (self.__length/self.__sampling_rate) - self.__fade_out - self.__silence_duration - self.__fade_in
        return self.__start_frequency, self.__stop_frequency, (sweep_duration*self.__sampling_rate)


class NovakSweepGenerator(object):
    def __init__(self, sampling_rate=48000.0, approx_length=2**16, start_frequency=20.0,
                 stop_frequency=20000.0, silence_duration=0.03, fade_out=0.02, fade_in=0.02):

        self.__sampling_rate = float(sampling_rate)
        self.__approx_length = float(approx_length)
        self.__start_frequency = float(start_frequency)
        self.__stop_frequency = float(stop_frequency)
        self.__silence_duration = float(silence_duration)
        self.__fade_out = float(fade_out*self.__sampling_rate)
        self.__fade_in = float(fade_in*self.__sampling_rate)

    def SetLength(self,length):
        self.__approx_length = float(length)

    def GetOutput(self):
        t = numpy.arange(0,round(self.__sampling_rate*self.GetLength()-1)/self.__sampling_rate,1/self.__sampling_rate)
        s = numpy.sin(2*numpy.pi*self.__start_frequency*self._GetSweepParameter()*(numpy.exp(t/self._GetSweepParameter())-1))
        if self.__fade_in > 0:
            s[0:self.__fade_in] = s[0:self.__fade_in] * ((-numpy.cos(numpy.arange(self.__fade_in)/self.__fade_in*math.pi)+1) / 2)
        if self.__fade_out > 0:
            s[-self.__fade_out:] = s[-self.__fade_out:] *  ((numpy.cos(numpy.arange(self.__fade_out)/self.__fade_out*numpy.pi)+1) / 2)
        return sumpf.Signal(channels=(s,),samplingrate=self.__sampling_rate,labels=("Sweep signal",))

    def _GetSweepParameter(self):
        L = 1/self.__start_frequency * round((self.__approx_length/self.__sampling_rate)*
                                             self.__start_frequency/numpy.log(self.__stop_frequency/self.__start_frequency))
        return L

    def GetLength(self):
        T_hat = self._GetSweepParameter()*numpy.log(self.__stop_frequency/self.__start_frequency)
        return T_hat

    def GetProperties(self):
        sweep_duration = self.GetLength() - self.__fade_out - self.__silence_duration - self.__fade_in
        return self.__start_frequency, self.__stop_frequency, (sweep_duration*self.__sampling_rate)
