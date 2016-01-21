import sumpf

class NLClipSignal(object):
    """
    Class to clip the signal nonlinearly and nonsymmetrically
    The input signal is clipped nonlinearly based on the power parameter. The power parameter should be a tuple of
    odd values. For value 1 it will hard clip the signal. For higher odd values it will clip the signal nonlinearly
    """
    def __init__(self, thresholds=(-1,1), signal=None, power=(1,1)):
        """
        :param thresholds: a tuple of thresholds to clip the signal
        :param signal: the input signal
        :param power: the power by which the input signal should be clipped
        :return:
        """
        self.__thresholds = thresholds
        if signal is None:
            self.__signal = sumpf.Signal
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
                if s <= self.__thresholds[0]:
                    channel.append(self.__thresholds[0])
                elif s >= self.__thresholds[1]:
                    channel.append(self.__thresholds[1])
                elif s < 0:
                    channel.append(s-(s**self.__power[0]/self.__power[0]))
                else:
                    channel.append(s-(s**self.__power[1]/self.__power[1]))
            channels.append(tuple(channel))
        return sumpf.Signal(channels=tuple(channels), labels=self.__signal.GetLabels())

    @sumpf.Input(tuple, "GetOutput")
    def SetThresholds(self, thresholds):
        self.__thresholds = thresholds

    @sumpf.Input(tuple, "GetOutput")
    def SetPower(self, power):
        self.__power = power