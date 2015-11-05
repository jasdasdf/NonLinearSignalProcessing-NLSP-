import sumpf

class ClipSignal(object):
    def __init__(self, thresholds, signal=None):
        self.__thresholds = thresholds
        if signal is None:
            self.__signal = sumpf.Signal

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
                    channel.append(self.__thresholds[0])
                elif s > self.__thresholds[1]:
                    channel.append(self.__thresholds[1])
                else:
                    channel.append(s)
            channels.append(tuple(channel))
        return sumpf.Signal(channels=tuple(channels), labels=self.__signal.GetLabels())

    @sumpf.Input(tuple, "GetOutput")
    def SetThresholds(self, thresholds):
        self.__thresholds = thresholds
