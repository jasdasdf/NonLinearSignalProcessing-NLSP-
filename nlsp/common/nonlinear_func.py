import sumpf
import sympy.mpmath as mpmath
import numpy
import collections

class NonlinearFunction(object):
    """
    Generates the nonlinear output of the input signal. The nonlinearity is introduced by the power series expansion or by applying
    orthogonal polynomials of the input signal.
    This NonlinearFunction class imports modules from sympy.mpmath to generate the orthogonal polynomials and this uses numpy.multiply to
    generate the power series expansion
    """

    @staticmethod
    def polynomials(degree,type):
            def power(channel,max_harm,method):
                if method == "power":
                    result = channel
                    for i in range(1, max_harm):
                        result = numpy.multiply(result, channel)
                    return result
                elif method == "hermite":
                    channell = []
                    for i in range(0,len(channel)):
                        channell.append(mpmath.hermite(max_harm,channel[i]))
                    return channell
                elif method == "chebyshev1":
                    channell = []
                    for i in range(0,len(channel)):
                        channell.append(mpmath.chebyt(max_harm,channel[i]))
                    return channell
                elif method == "chebyshev2":
                    channell = []
                    for i in range(0,len(channel)):
                        channell.append(mpmath.chebyu(max_harm,channel[i]))
                    return channell
                elif method == "legendre":
                    channell = []
                    for i in range(0,len(channel)):
                        channell.append(mpmath.legendre(max_harm,channel[i]))
                    return channell
                elif method == "laguerre":
                    channell = []
                    for i in range(0,len(channel)):
                        channell.append(mpmath.laguerre(max_harm,channel[i]))
                    return channell
            return NonlinearFunction(nonlin_func=type, max_harm=degree, func=power)

    def __init__(self, signal=None, nonlin_func=lambda x: x, max_harm=1, func=None):
        """
        :param signal: the input Signal
        :param nonlin_func: a callable object, that expects the polynomial class which has the parameters degree and
                            type. The degree is the order of the polynomials which should be produced and
                            the type is a string which may be power, hermite, chebyshev1, chebyshev2, legendre or
                            laguerre based on the type of polynomials which should be produced
        :param max_harm: the maximum produced harmonic of the nonlinear distortion
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__nonlin_func = nonlin_func
        self.__func = func
        self.__max_harm = max_harm

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.__signal = signal

    @sumpf.Input(collections.Callable, "GetOutput")
    def SetNonlinearFunction(self, nonlin_func):
        self.__nonlin_func = nonlin_func

    @sumpf.Input(int,("GetMaximumHarmonic","GetOutput"))
    def SetMaximumHarmonic(self, max_harm):
        self.__max_harm = max_harm


    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        new_channels = []
        for c in self.__signal.GetChannels():
            self.__dummy = c
            new_channels.append(tuple(self.__func(c,self.__max_harm,self.__nonlin_func)))
        return sumpf.Signal(channels=new_channels, samplingrate=self.__signal.GetSamplingRate(), labels=self.__signal.GetLabels())

    @sumpf.Output(int)
    def GetMaximumHarmonic(self):
        return self.__max_harm
