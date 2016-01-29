import sumpf
import nlsp

class CalculateIR(object):
    """
    calculates the impulse response of the blackbox, given the input and output. It uses the Regularized spectral
    inversion class of sumpf to calculate the impulse response of the output
    """
    def __init__(self, input=None, output=None):
        if input is None:
            self.__input = sumpf.Signal()
        else:
            self.__input = input
        if output is None:
            self.__output = self.__input
        else:
            self.__output = output

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetInput(self, ip_signal):
        self.__input = ip_signal

    @sumpf.Input(sumpf.Signal, "GetOutput")
    def SetOutput(self, op_signal):
        self.__output = op_signal

    @sumpf.Output(sumpf.Signal)
    def GetOutput(self):
        ip_spec = sumpf.modules.FourierTransform(signal=self.__input).GetSpectrum()
        op_spec = sumpf.modules.FourierTransform(signal=self.__output).GetSpectrum()
        ip_spec_invert = sumpf.modules.RegularizedSpectrumInversion(spectrum=ip_spec).GetOutput()
        tf = sumpf.modules.MultiplySpectrums(spectrum1=ip_spec_invert, spectrum2=op_spec).GetOutput()
        op = sumpf.modules.InverseFourierTransform(spectrum=tf).GetSignal()
        return op

