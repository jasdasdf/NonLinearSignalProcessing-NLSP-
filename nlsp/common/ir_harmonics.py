import sumpf
import nlsp


class IR_harmonics(object):
    """
    A class to generate the inpulse response of the harmonics using nonlinear convolution method
    """
    def __init__(self, impulse_response=None, harmonic=1):
        """
        :param input_signal: the input signal
        :param harmonic: the harmonic whose impulse response has to be found
        :return:
        """
        if impulse_response is None:
            self.__impulse_response = sumpf.Signal()
        else:
            self.__impulse_response = impulse_response
        self.__harmonic = harmonic
        self.__getharmir = sumpf.modules.FindHarmonicImpulseResponse()
        self.__resampler = sumpf.modules.ResampleSignal()

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetImpulseResponse(self, signal):
        self.__impulse_response = signal

    @sumpf.Input(int,"GetOutput","GetHarmonic")
    def SetHarmonic(self, harmonic):
        self.__harmonic = harmonic

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):


    @sumpf.Output(int)
    def GetHarmonic(self):
        return self.__harmonic