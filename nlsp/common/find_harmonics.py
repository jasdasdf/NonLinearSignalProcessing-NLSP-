import math
import numpy
import sumpf
import nlsp

class FindHarmonicImpulseResponse_Novak(object):
    """
    Calculates the impulse response of a harmonic from a given impulse response.

    To make this possible, the given full impulse response must have been measured
    with a sweep whose frequency increases exponentially over time. This makes
    the time difference between the excitation of a certain frequency by nonlinear
    distortion and its later excitation by the sweep independent of the frequency,
    so that the impulse responses of the harmonics occur as peaks in the non causal
    part of the at the full impulse response. If the deconvolution is done by
    division in the frequency domain, these non causal artifacts are "wrapped around"
    to the end of the impulse response.

    The peaks, that have been cut out of the full impulse response, are time stretched
    to become the impulse response of the harmonic. This becomes clear, when considering
    that the spectrum of the unscaled impulse response of the n-th harmonic would
    be a transfer function in dependency of n times the frequency. Therefore, the
    resulting impulse response has a sampling rate, that is n times smaller than
    that of the original impulse response and may have to be resampled.

    To locate the impulse responses of the harmonics, the sweep rate of the excitation
    signal has to be known. This rate can be calculated by the sweep's start frequency,
    its stop frequency and the time it took to sweep between the two.
    """
    def __init__(self,
                 impulse_response=None,
                 harmonic_order=2,
                 sweep_generator=None):
        """
        @param impulse_response: the impulse response Signal, from which the impulse responses of the harmonics shall be cut out
        @param harmonic_order: the integer order of the harmonic, whose impulse response shall be determined
        @param sweep_start_frequency: the start frequency of the exponential sweep, that has been used to measure the given impulse response
        @param sweep_stop_frequency: the stop frequency of the exponential sweep, that has been used to measure the given impulse response
        @param sweep_duration: the time in seconds that it took the sweep to go from the start frequency to the stop frequency
        """
        if sweep_generator is None:
            self.__sweep_generator = nlsp.NovakSweepGenerator()
        else:
            self.__sweep_generator = sweep_generator
        if harmonic_order < 2:
            raise ValueError("The harmonic order has to be at least 2.")
        self.__impulse_response = impulse_response
        if impulse_response is None:
            self.__impulse_response = sumpf.modules.ImpulseGenerator().GetSignal()
        self.__harmonic_order = harmonic_order
        self.__sweep_start_frequency = self.__sweep_generator.GetStartFrequency()
        self.__sweep_stop_frequency = self.__sweep_generator.GetStopFrequency()
        self.__sweep_duration = self.__sweep_generator.GetLength()/self.__sweep_generator.GetOutput().GetSamplingRate()
        self.__sweep_parameter = self.__sweep_generator.GetSweepParameter()
        self.__sampling_rate = self.__impulse_response.GetSamplingRate()

    @sumpf.Input(sumpf.Signal, "GetHarmonicImpulseResponse")
    def SetImpulseResponse(self, impulse_response):
        """
        Sets the impulse response from which the impulse response of the harmonic
        shall be cut out.
        @param impulse_response: a Signal instance
        """
        self.__impulse_response = impulse_response

    @sumpf.Input(int, "GetHarmonicImpulseResponse")
    def SetHarmonicOrder(self, order):
        """
        Sets the order of the harmonic, whose impulse response shall be determined.
        The given order has to be at least two. To separate the impulse response
        of the fundamental from the measured nonlinearities, use the CutSignal
        and the WindowGenerator classes.
        @param order: the order as an integer (at least 2)
        """
        if order < 2:
            raise ValueError("The harmonic order has to be at least 2.")
        self.__harmonic_order = order

    @sumpf.Input(float, "GetHarmonicImpulseResponse")
    def SetSweepStartFrequency(self, frequency):
        """
        Sets the start frequency of the sweep, with which the given impulse response
        has been recorded and calculated.
        @param frequency: the frequency in Hertz as a float
        """
        self.__sweep_start_frequency = frequency

    @sumpf.Input(float, "GetHarmonicImpulseResponse")
    def SetSweepStopFrequency(self, frequency):
        """
        Sets the stop frequency of the sweep, with which the given impulse response
        has been recorded and calculated.
        @param frequency: the frequency in Hertz as a float
        """
        self.__sweep_stop_frequency = frequency

    @sumpf.Input(float, "GetHarmonicImpulseResponse")
    def SetSweepDuration(self, duration):
        """
        Sets the time that it took the sweep to go from its start frequency to
        its stop frequency.
        If the duration is set to None, it is assumed, that the sweep duration
        is the same as the duration of the given impulse response.
        @param frequency: the time in seconds as a float or None
        """
        self.__sweep_duration = duration

    @sumpf.Output(sumpf.Signal)
    def GetHarmonicImpulseResponse(self):
        """
        Cuts the impulse response of the harmonic out of the given full impulse
        response and scales to the correct length.
        Note that the returned impulse response is shorter than the full impulse
        response and might have to be extended with zeros.
        @retval : the harmonic impulse response as a Signal
        """
        # get the sample indices between the impulse response can be found
        # sweep_duration = self.__sweep_duration
        # if sweep_duration is None:
        #     sweep_duration = self.__impulse_response.GetDuration()
        # sweep_rate = (self.__sweep_stop_frequency / self.__sweep_start_frequency) ** (1.0 / sweep_duration)
        # harmonic_start_time = self.__impulse_response.GetDuration() - math.log(self.__harmonic_order, sweep_rate)
        # harmonic_start_sample = sumpf.modules.DurationToLength(duration=harmonic_start_time, samplingrate=self.__impulse_response.GetSamplingRate(), even_length=False).GetLength()
        # harmonic_stop_sample = len(self.__impulse_response)
        # if self.__harmonic_order > 2:
        #     harmonic_stop_time = self.__impulse_response.GetDuration() - math.log(self.__harmonic_order - 1, sweep_rate)
        #     harmonic_stop_sample = sumpf.modules.DurationToLength(duration=harmonic_stop_time, samplingrate=self.__impulse_response.GetSamplingRate(), even_length=False).GetLength()
        # # prepare the labels
        # labels = []
        # affix = " (%s harmonic)" % sumpf.helper.counting_number(self.__harmonic_order)
        # for l in self.__impulse_response.GetLabels():
        #     if l is None:
        #         labels.append("Impulse Response" + affix)
        #     else:
        #         labels.append(l + affix)
        # # crop to the impulse response of the wanted harmonic
        # cropped = self.__impulse_response[harmonic_start_sample:harmonic_stop_sample-200]
        # harmonic = sumpf.Signal(channels=cropped.GetChannels(), samplingrate=cropped.GetSamplingRate() / self.__harmonic_order, labels=tuple(labels))
        # if len(harmonic) % 2 != 0:
        #     harmonic = sumpf.Signal(channels=tuple([c + (0.0,) for c in harmonic.GetChannels()]), samplingrate=harmonic.GetSamplingRate(), labels=harmonic.GetLabels())

        L = self.__sweep_parameter
        N = self.__harmonic_order
        fs = self.__sampling_rate
        len_Hammer = 2**12
        h = self.__impulse_response.GetChannels()[0]
        h = numpy.asarray(h)

        # positions of higher orders up to N
        dt = L*numpy.log(numpy.arange(1,N+1))*fs

        # The time lags may be non-integer in samples, the non integer delay must be applied later
        dt_rem = dt - numpy.around(dt)

        # number of samples to make an artificail delay
        posun = round(len_Hammer/2)
        h_pos = numpy.hstack((h, h[0:posun + len_Hammer - 1]))

        # separation of higher orders
        hs = numpy.zeros((N,len_Hammer))

        # frequency axis
        axe_w = numpy.linspace(0, numpy.pi, num=len_Hammer/2+1);

        merger = sumpf.modules.MergeSignals()
        for k in range(N):
            hs[k,:] = h_pos[len(h)-round(dt[k])-posun-1:len(h)-round(dt[k])-posun+len_Hammer-1]
            H_temp = numpy.fft.rfft(hs[k,:])

            # Non integer delay application
            H_temp = H_temp * numpy.exp(-1j*dt_rem[k]*axe_w)
            harm = numpy.fft.irfft(H_temp)
            harm = sumpf.Signal(channels=(harm,),samplingrate=self.__sampling_rate,labels=("harmonics",))
            merger.AddInput(harm)
        return merger.GetOutput()
