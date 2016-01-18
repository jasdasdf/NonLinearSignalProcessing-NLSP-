import numpy
import mpmath

def power_series(degree):
    def func(channel):
        result = channel
        for i in range(1, degree):
            result = numpy.multiply(result, channel)
        return result
    return func

def legrendre_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(mpmath.legendre(degree,channel[i]))
        return channell
    return func

def chebyshev1_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(mpmath.chebyt(degree,channel[i]))
        return channell
    return func

def chebyshev2_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(mpmath.chebyu(degree,channel[i]))
        return channell
    return func

def hermite_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(mpmath.hermite(degree,channel[i]))
        return channell
    return func

def laguerre_polynomial(degree):
    def func(channel):
        channell = []
        for i in range(0,len(channel)):
            channell.append(mpmath.laguerre(degree,channel[i]))
        return channell
    return func