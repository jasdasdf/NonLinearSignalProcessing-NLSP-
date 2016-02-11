import numpy
import sumpf
import nlsp
import common.plot as plot

class NLConvolution(object):

    def __init__(self,input_sweep, output_sweep, sweep_start_freq=20.0, sweep_stop_freq=20000.0, sweep_length=None,
                 branches=5):
        if input_sweep is None:
            self.__input = sumpf.Signal()
        else:
            self.__input = input_sweep
        if output_sweep is None:
            self.__output = sumpf.Signal()
        else:
            self.__output = output_sweep
        self.__direct_length = 500
        self.__start_freq = sweep_start_freq
        self.__stop_freq = sweep_stop_freq
        self.__branches = branches
        if sweep_length is None:
            self.__length = len(self.__input)
        else:
            self.__length = sweep_length
        self.__harmonics_spec = []
        self.__harmonics_ir = []
        self.__harmonic_kernel_1 = []
        self.__harmonic_kernel_2 = []
        self.__input_stage = sumpf.modules.AmplifySignal(input=self.__input)
        self.__output_stage = sumpf.modules.AmplifySignal(input=self.__output)
        self.__invert_spec = sumpf.modules.RegularizedSpectrumInversion(start_frequency=self.__start_freq,
                                                                        stop_frequency=self.__stop_freq)
        self.__multiply = sumpf.modules.MultiplySpectrums()
        self.__transform1 = sumpf.modules.FourierTransform()
        self.__transform2 = sumpf.modules.FourierTransform()
        self.__itransform = sumpf.modules.InverseFourierTransform()
        self.__merge_ir = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
        self.__cut_signal = sumpf.modules.CutSignal(stop=self.__direct_length)
        self.__find_harmonic = sumpf.modules.FindHarmonicImpulseResponse(sweep_start_frequency=self.__start_freq,
                                                                         sweep_stop_frequency=self.__stop_freq,
                                                                         sweep_duration=self.__length/self.__input.GetSamplingRate())
        # signal processing chain
        sumpf.connect(self.__input_stage.GetOutput, self.__transform1.SetSignal)
        sumpf.connect(self.__transform1.GetSpectrum, self.__invert_spec.SetSpectrum)
        sumpf.connect(self.__output_stage.GetOutput, self.__transform2.SetSignal)
        sumpf.connect(self.__invert_spec.GetOutput, self.__multiply.SetInput1)
        sumpf.connect(self.__transform2.GetSpectrum, self.__multiply.SetInput2)
        sumpf.connect(self.__multiply.GetOutput, self.__itransform.SetSpectrum)
        sumpf.connect(self.__itransform.GetSignal, self.__cut_signal.SetInput)
        sumpf.connect(self.__itransform.GetSignal, self.__find_harmonic.SetImpulseResponse)
        sumpf.connect(self.__cut_signal.GetOutput, self.__merge_ir.AddInput)
        for branch in range(2,self.__branches+1):
            self.__find_harmonic.SetHarmonicOrder(branch)
            self.__merge_ir.AddInput(sumpf.Signal(channels=self.__find_harmonic.GetHarmonicImpulseResponse().GetChannels(),
                                                  samplingrate=self.__input.GetSamplingRate(),
                                                  labels=self.__find_harmonic.GetHarmonicImpulseResponse().GetLabels()))
        self.__merge_tf = sumpf.modules.FourierTransform(self.__merge_ir.GetOutput()).GetSpectrum()
        for i in range(len(self.__merge_tf.GetChannels())):
            tf_harmonics =  sumpf.modules.SplitSpectrum(data=self.__merge_tf, channels=[i]).GetOutput()
            self.__harmonics_ir.append(sumpf.modules.InverseFourierTransform(tf_harmonics).GetSignal())
            self.__harmonics_spec.append(tf_harmonics)

    def GetPower_filter_1(self):
        if len(self.__harmonics_spec) != 5:
            self.__harmonics_spec.extend([sumpf.modules.ConstantSpectrumGenerator(value=0.0,
                                                                                  resolution=self.__harmonics_spec[0].GetResolution(),
                                                                                  length=len(self.__harmonics_spec[0])).GetSpectrum()]*(5-len(self.__harmonics_spec)))
        Volterra_tf = []
        Volterra_tf.append(self.__harmonics_spec[0] + (3)*self.__harmonics_spec[2] +(5)*self.__harmonics_spec[4])
        Volterra_tf.append(sumpf.modules.AmplifySpectrum(input=self.__harmonics_spec[1],factor=2j).GetOutput() +
                 sumpf.modules.AmplifySpectrum(input=self.__harmonics_spec[3],factor=8j).GetOutput())
        Volterra_tf.append(-4*self.__harmonics_spec[2] - 20*self.__harmonics_spec[4])
        Volterra_tf.append(sumpf.modules.AmplifySpectrum(input=self.__harmonics_spec[3],factor=-8j).GetOutput())
        Volterra_tf.append(16*self.__harmonics_spec[4])
        for kernel in Volterra_tf:
            ift = sumpf.modules.InverseFourierTransform(spectrum=kernel).GetSignal()
            self.__harmonic_kernel_1.append(ift)
        return self.__harmonic_kernel_1[:self.__branches]

    def GetPower_filter_2(self):
        Volterra_tf = []
        Volterra_tf.append(self.__harmonics_spec[0] + (3/4)*self.__harmonics_spec[2] +(5/8)*self.__harmonics_spec[4])
        Volterra_tf.append(sumpf.modules.AmplifySpectrum(input=self.__harmonics_spec[1],factor=-1j/2).GetOutput() +
                 sumpf.modules.AmplifySpectrum(input=self.__harmonics_spec[3],factor=-1j/2).GetOutput())
        Volterra_tf.append((-1/4)*self.__harmonics_spec[2] - (5/16)*self.__harmonics_spec[4])
        Volterra_tf.append(sumpf.modules.AmplifySpectrum(input=self.__harmonics_spec[3],factor=(1j/8)).GetOutput())
        Volterra_tf.append((1/16)*self.__harmonics_spec[4])
        for kernel in Volterra_tf:
            ift = sumpf.modules.InverseFourierTransform(spectrum=kernel).GetSignal()
            self.__harmonic_kernel_2.append(ift)
        return self.__harmonic_kernel_2

    def GetPower_filter_auto(self):
        spec = []
        spec_c = []
        for order in range(1,self.__branches+1):
            def chebyshev(n):
                if n == 0:
                    return (1.0,)
                elif n == 1:
                    return (0.0, 1.0)
                else:
                    return tuple(numpy.subtract(numpy.multiply((0.0,) + chebyshev(n - 1), 2.0), chebyshev(n - 2) + (0.0, 0.0)))
            print order,chebyshev(order)
            weighted = []
            for i, factor in enumerate(chebyshev(order)[1:]):
                # print order,i,factor
                if factor != 0.0:
                    weighted.append(self.__harmonics_spec[i] * factor)
            result = weighted[0]
            for s in weighted[1:]:
                result += s
            spec.append(result)
        for kernel in spec:
            ift = sumpf.modules.InverseFourierTransform(spectrum=kernel).GetSignal()
            spec_c.append(ift)
        return spec_c

    def GetCheby_filter(self):
        return self.__harmonics_ir