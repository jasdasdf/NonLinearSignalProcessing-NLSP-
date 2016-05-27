import sumpf

class RemoveOutliers(object):
    def __init__(self, thresholds, signal=None, value=0):
        self.__thresholds = thresholds
        self.__value = value
        if signal is None:
            self.__signal = sumpf.Signal
        else:
            self.__signal = signal

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, signal):
        self.__signal = signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        channels = []
        for c in self.__signal.GetChannels():
            channel = []
            for s in c:
                if s < self.__thresholds[0]:
                    channel.append(self.__value)
                elif s > self.__thresholds[1]:
                    channel.append(self.__value)
                else:
                    channel.append(s)
            channels.append(tuple(channel))
        return sumpf.Signal(channels=tuple(channels), labels=self.__signal.GetLabels())

    @sumpf.Input(tuple, "GetOutput")
    def SetThresholds(self, thresholds):
        self.__thresholds = thresholds
