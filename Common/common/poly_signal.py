import sumpf

class PolynomialOfSignal(object):
    def __init__(self, signal=None, power=None):
        if signal is None:
            self.__signal = sumpf.Signal
        else:
            self.__signal = signal
        if power is None:
            self.__power = 1
        else:
            self.__power = power

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.__signal = signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        signal = self.__signal
        for i in range(1,self.__power):
            signal = self.__signal * signal
        return signal


