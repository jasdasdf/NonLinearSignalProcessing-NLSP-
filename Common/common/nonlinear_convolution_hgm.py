import sumpf
import common
import head_specific

class NonlinearConvolutionHgm(object):
    def __init__(self, excitation=None, response=None, length=None, samplingrate=None):
        self.__excitation = excitation
        self.__response = response
        self.__length = length
        self.__samplingrate = samplingrate
        self.__branches = 5
        self.__powers = []
        self.__ffts = []
        self.__filterspec = []
        self.__iffts = []
        self.__sums = [None] * self.__branches
        sweep_start_frequency, sweep_stop_frequency, sweep_duration = head_specific.get_sweep_properties(sumpf.modules.SilenceGenerator(length=length, samplingrate=samplingrate).GetSignal())
        fft_excitation = sumpf.modules.FourierTransform()
        sumpf.connect(self.__excitation.GetOutput, fft_excitation.SetSignal)
        fft_response = sumpf.modules.FourierTransform()
        sumpf.connect(self.__response.GetOutput, fft_response.SetSignal)
        inversion = sumpf.modules.RegularizedSpectrumInversion(start_frequency=max(sweep_start_frequency*4.0, 20.0),stop_frequency=sweep_stop_frequency/4.0,transition_length=100,epsilon_max=0.1)
        sumpf.connect(fft_excitation.GetSpectrum,inversion.SetSpectrum)
        tf_measured = sumpf.modules.MultiplySpectrums()
        sumpf.connect(inversion.GetOutput, tf_measured.SetInput1)
        sumpf.connect(fft_response.GetSpectrum,tf_measured.SetInput2)
        ir_measured = sumpf.modules.InverseFourierTransform()
        sumpf.connect(tf_measured.GetOutput,ir_measured.SetSpectrum)
        h1_measured = sumpf.modules.CutSignal(start=0, stop=4096)
        sumpf.connect(ir_measured.GetSignal,h1_measured.SetInput)
        h2_measured = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=2,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
        sumpf.connect(ir_measured.GetSignal,h2_measured.SetImpulseResponse)
        h3_measured = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=3,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
        sumpf.connect(ir_measured.GetSignal,h3_measured.SetImpulseResponse)
        h4_measured = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=4,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
        sumpf.connect(ir_measured.GetSignal,h4_measured.SetImpulseResponse)
        h5_measured = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=5,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
        sumpf.connect(ir_measured.GetSignal,h5_measured.SetImpulseResponse)
        H1_measured = sumpf.modules.FourierTransform()
        sumpf.connect(h1_measured.GetOutput,H1_measured.SetSignal)
        H2_measured = sumpf.modules.FourierTransform()
        sumpf.connect(h2_measured.GetHarmonicImpulseResponse,H2_measured.SetSignal)
        H3_measured = sumpf.modules.FourierTransform()
        sumpf.connect(h3_measured.GetHarmonicImpulseResponse,H3_measured.SetSignal)
        H4_measured = sumpf.modules.FourierTransform()
        sumpf.connect(h4_measured.GetHarmonicImpulseResponse,H4_measured.SetSignal)
        H5_measured = sumpf.modules.FourierTransform()
        sumpf.connect(h5_measured.GetHarmonicImpulseResponse,H5_measured.SetSignal)
        common.plot.plot(h1_measured.GetOutput())
        common.plot.plot(ir_measured.GetSignal())
        common.plot.log()
        common.plot.plot(H1_measured.GetSpectrum(),show=False)
        common.plot.plot(H2_measured.GetSpectrum(),show=False)
        common.plot.plot(H3_measured.GetSpectrum(),show=False)
        common.plot.plot(H4_measured.GetSpectrum(),show=False)
        common.plot.plot(H5_measured.GetSpectrum())

#         for branch,spectrum in enumerate():
#             p = common.PolynomialOfSignal(power=branch+1,signal=self.__signal)
#             t = sumpf.modules.FourierTransform()
#             f = sumpf.modules.MultiplySpectrums(spectrum2=spectrum)
#             i = sumpf.modules.InverseFourierTransform()
#             sumpf.connect(p.GetOutput, t.SetSignal)
#             sumpf.connect(t.GetSpectrum, f.SetInput1)
#             sumpf.connect(f.GetOutput, i.SetSpectrum)
#             self.__powers.append(p)
#             self.__ffts.append(t)
#             self.__filterspec.append(f)
#             self.__iffts.append(i)
#         for i in reversed(range(len(self.__filterspec)-1)):
#             a = sumpf.modules.AddSignals()
# #            print "connecting ifft %i to adder %i" % (i, i)
#             sumpf.connect(self.__iffts[i].GetSignal, a.SetInput1)
#             if i == len(self.__filterspec)-2:
# #                print "connecting ifft %i to adder %i" % (i+1, i)
#                 sumpf.connect(self.__iffts[i+1].GetSignal, a.SetInput2)
#             else:
# #                print "connecting adder %i to adder %i" % (i+1, i)
#                 sumpf.connect(self.__sums[i+1].GetOutput, a.SetInput2)
#             self.__sums[i] = a
#
#         # make the input and output methods of the signal processing chain available
#         self.SetInput = p.SetInput
#         self.GetOutput = self.__sums[0].GetOutput
#
#     def SetParameters(self, filters):
#         pairs = []
#         for i, f in enumerate(filters):
#             pairs.append((self.__filterspec[i].SetInput2, f))
#         sumpf.set_multiple_values(pairs)
