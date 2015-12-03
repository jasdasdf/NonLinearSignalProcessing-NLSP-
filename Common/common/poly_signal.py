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
        channels = []
        for c in self.__signal.GetChannels():
            channel = []
            for s in c:
                channel.append(s**self.__power)
            channels.append(tuple(channel))
        return sumpf.Signal(channels=tuple(channels), labels=self.__signal.GetLabels())


