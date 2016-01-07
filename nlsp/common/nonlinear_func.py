import sumpf
import sympy.mpmath as mpmath
import numpy

class NonlinearFunction(object):
    """
    Generates the nonlinear output of the input signal. The nonlinearity is introduced by the power series expansion or by applying
    orthogonal polynomials of the input signal
    """

    @staticmethod
    def power_series(degree):
        def func(channel):
            result = channel
            for i in range(1, degree):
                result = numpy.multiply(result, channel)
            return result
        return NonlinearFunction(nonlin_func=func, max_harm=degree)

    @staticmethod
    def hermite_polynomial(degree):
        def func(channel):
            channell = []
            for i in range(0,len(channel)):
                channell.append(mpmath.hermite(degree,channel[i]))
            return channell
        return NonlinearFunction(nonlin_func=func, max_harm=degree)

    @staticmethod
    def legrendre_polynomial(degree):
        def func(channel):
            channell = []
            for i in range(0,len(channel)):
                channell.append(mpmath.legendre(degree,channel[i]))
            return channell
        return NonlinearFunction(nonlin_func=func, max_harm=degree)

    @staticmethod
    def chebyshev1_polynomial(degree):
        def func(channel):
            channell = []
            for i in range(0,len(channel)):
                channell.append(mpmath.chebyt(degree,channel[i]))
            return channell
        return NonlinearFunction(nonlin_func=func, max_harm=degree)

    @staticmethod
    def chebyshev2_polynomial(degree):
        def func(channel):
            channell = []
            for i in range(0,len(channel)):
                channell.append(mpmath.chebyu(degree,channel[i]))
            return channell
        return NonlinearFunction(nonlin_func=func, max_harm=degree)

    @staticmethod
    def laguerre_polynomial(degree):
        def func(channel):
            channell = []
            for i in range(0,len(channel)):
                channell.append(mpmath.laguerre(degree,channel[i]))
            return channell
        return NonlinearFunction(nonlin_func=func, max_harm=degree)

    def __init__(self, signal=None, nonlin_func=lambda x: x, max_harm=1):
        """
        :param signal: the input Signal
        :param nonlin_func: a callable object, that expects a Signal's channel as an iterable, and returns a nonlinear distorted version of it
        :param max_harm: the maximum produced harmonic of the nonlinear distortion
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__nonlin_func = nonlin_func
        self.__max_harm = max_harm

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.__signal = signal

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetNonlinearFunction(self, nonlin_func):
        self.__nonlin_func = nonlin_func

    @sumpf.Input(int,"GetMaximumHarmonic")
    def SetMaximumHarmonic(self, max_harm):
        self.__max_harm = max_harm

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        new_channels = []
        for c in self.__signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(self.__nonlin_func(c)))
        return sumpf.Signal(channels=new_channels, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

    @sumpf.Output(int)
    def GetMaximumHarmonic(self):
        return self.__max_harm
