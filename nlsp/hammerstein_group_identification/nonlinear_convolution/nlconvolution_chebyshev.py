import sumpf
import nlsp
import numpy
import math
import common.plot as plot

def nonlinearconvolution_chebyshev_spectralinversion(sweep_generator, output_sweep, branches=5):
    """
    System Identification using Nonlinear Convolution (spectral Inversion method)
    :param sweep_generator: the object of sweep generator class
    :param output_sweep: the output signal from the reference nonlinear system
    :return: the parameters of HGM (filter kernels and nonlinear functions)
    """
    sweep_length = sweep_generator.GetLength()
    sweep_start_freq = sweep_generator.GetStartFrequency()
    sweep_stop_freq = sweep_generator.GetStopFrequency()
    input_sweep = sweep_generator.GetOutput()

    if isinstance(input_sweep ,(sumpf.Signal)):
        ip_signal = input_sweep
        ip_spectrum = sumpf.modules.FourierTransform(signal=input_sweep).GetSpectrum()
    else:
        ip_signal = sumpf.modules.InverseFourierTransform(spectrum=input_sweep).GetSignal()
        ip_spectrum = input_sweep
    if isinstance(output_sweep ,(sumpf.Signal)):
        op_spectrum = sumpf.modules.FourierTransform(signal=output_sweep).GetSpectrum()
    else:
        op_spectrum = output_sweep
    inversed_ip = sumpf.modules.RegularizedSpectrumInversion(spectrum=ip_spectrum,start_frequency=sweep_start_freq,
                                                             stop_frequency=sweep_stop_freq).GetOutput()
    tf_sweep = sumpf.modules.MultiplySpectrums(spectrum1=inversed_ip, spectrum2=op_spectrum).GetOutput()
    ir_sweep = sumpf.modules.InverseFourierTransform(spectrum=tf_sweep).GetSignal()

    # Novaks method
    # ir_harmonics_all = nlsp.FindHarmonicImpulseResponse_Novak(ir_sweep,harmonic_order=branches,sweep_generator=sweep_generator)
    # ir_merger = ir_harmonics_all.GetHarmonicImpulseResponse()

    # Jonas method
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)
    for i in range(branches-1):
        split_harm = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=ir_sweep,
                                                               harmonic_order=i+2,
                                                               sweep_start_frequency=sweep_start_freq,
                                                               sweep_stop_frequency=sweep_stop_freq,
                                                               sweep_duration=(sweep_length/ip_signal.GetSamplingRate())).GetHarmonicImpulseResponse()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=split_harm.GetLabels()))
    ir_merger = ir_merger.GetOutput()

    Volterra_ir = []
    for i in range(len(ir_merger.GetChannels())):
        ir_harmonics =  sumpf.modules.SplitSignal(data=ir_merger, channels=[i]).GetOutput()
        Volterra_ir.append(ir_harmonics)
    nl_func = nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)
    return Volterra_ir, nl_func


def nonlinearconvolution_chebyshev_temporalreversal(sweep_generator, output_sweep, branches=5):
    """
    System Identification using Nonlinear Convolution (Temporal Reversal method)
    :param sweep_generator: the object of sweep generator class
    :param output_sweep: the output signal from the reference nonlinear system
    :return: the parameters of HGM (filter kernels and nonlinear functions)
    """
    sweep_length = sweep_generator.GetLength()
    sweep_start_freq = sweep_generator.GetStartFrequency()
    sweep_stop_freq = sweep_generator.GetStopFrequency()
    ip_signal = sweep_generator.GetOutput()

    output_sweep_channel = output_sweep.GetChannels()[0]
    sampling_rate = output_sweep.GetSamplingRate()
    sweep_parameter = sweep_generator.GetSweepParameter()
    output_sweep_channel_mean_sub = output_sweep_channel - numpy.mean(output_sweep_channel)
    fft_len = int(2**numpy.ceil(numpy.log2(len(output_sweep_channel_mean_sub))))
    output_sweep_channel_spec = numpy.fft.rfft(output_sweep_channel_mean_sub,fft_len)/sampling_rate
    interval = numpy.linspace(0, sampling_rate/2, num=fft_len/2+1)
    inverse_sweep = 2*numpy.sqrt(interval/sweep_parameter)*numpy.exp(1j*(2*numpy.pi*sweep_parameter*interval*(sweep_start_freq/interval +
                                                                 numpy.log(interval/sweep_start_freq) - 1) + numpy.pi/4))
    inverse_sweep[0] = 0j
    tf_sweep_channel = output_sweep_channel_spec*inverse_sweep
    ir_sweep_channel = numpy.fft.irfft(tf_sweep_channel)
    ir_sweep = sumpf.Signal(channels=(ir_sweep_channel,),samplingrate=sampling_rate,labels=("Sweep signal",))

    # Novaks method
    # ir_harmonics_all = nlsp.FindHarmonicImpulseResponse_Novak(ir_sweep,harmonic_order=branches,sweep_generator=sweep_generator)
    # ir_merger = ir_harmonics_all.GetHarmonicImpulseResponse()

    # Jonas method
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)
    for i in range(branches-1):
        split_harm = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=ir_sweep,
                                                               harmonic_order=i+2,
                                                               sweep_start_frequency=sweep_start_freq,
                                                               sweep_stop_frequency=sweep_stop_freq,
                                                               sweep_duration=(sweep_length/ip_signal.GetSamplingRate())).GetHarmonicImpulseResponse()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=split_harm.GetLabels()))
    ir_merger = ir_merger.GetOutput()

    Volterra_ir = []
    for i in range(len(ir_merger.GetChannels())):
        ir_harmonics =  sumpf.modules.SplitSignal(data=ir_merger, channels=[i]).GetOutput()
        Volterra_ir.append(ir_harmonics)
    nl_func = nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)
    return Volterra_ir, nl_func
