import sumpf

class NLClipSignal(object):
    """
    Class to clip the signal nonlinearly
    The input signal is clipped nonlinearly based on the power parameter. The lower the power parameter the higher
    the clipping effect will be.
    """
    def __init__(self, signal=None, thresholds=(-1,1), power=1.0):
        """
        :param thresholds: a tuple of thresholds to clip the signal
        :param signal: the input signal
        :param power: the power by which the input signal should be clipped. The lower the power the higher the clipping
        :return:
        """
        self.__thresholds = thresholds
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
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
                else:
                    channel.append((1-(abs(s)/self.__power))*s)
            channels.append(tuple(channel))
        return sumpf.Signal(channels=tuple(channels), labels=self.__signal.GetLabels())

    @sumpf.Input(tuple, "GetOutput")
    def SetThresholds(self, thresholds):
        self.__thresholds = thresholds

    @sumpf.Input(float, "GetOutput")
    def SetPower(self, power):
        self.__power = power