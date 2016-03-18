import sumpf
import nlsp
import adaptfilt
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
        split_harm = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=ir_sweep,
                                                            harmonic_order=i+2,
                                                            sweep_generator=sweep_generator).GetHarmonicImpulseResponse()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=split_harm.GetLabels()))
    ir_merger = ir_merger.GetOutput()

    Volterra_ir = []
    for i in range(len(ir_merger.GetChannels())):
        ir_harmonics =  sumpf.modules.SplitSignal(data=ir_merger, channels=[i]).GetOutput()
        Volterra_ir.append(nlsp.relabel(ir_harmonics,"%r harmonic identified csi" %str(i+1)))
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

    # output_sweep = nlsp.append_zeros(output_sweep)
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(output_sweep).GetSpectrum()
    out_spec = out_spec / output_sweep.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()

    # Novaks method
    # ir_harmonics_all = nlsp.FindHarmonicImpulseResponse_Novak(ir_sweep,harmonic_order=branches,sweep_generator=sweep_generator)
    # ir_merger = ir_harmonics_all.GetHarmonicImpulseResponse()

    # Jonas method
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)
    for i in range(branches-1):
        split_harm = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=ir_sweep,
                                                            harmonic_order=i+2,
                                                            sweep_generator=sweep_generator).GetHarmonicImpulseResponse()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=split_harm.GetLabels()))
    ir_merger = ir_merger.GetOutput()
    # nlsp.common.plots.plot(ir_merger)
    Volterra_ir = []
    for i in range(len(ir_merger.GetChannels())):
        ir_harmonics =  sumpf.modules.SplitSignal(data=ir_merger, channels=[i]).GetOutput()
        Volterra_ir.append(nlsp.relabel(ir_harmonics,"%r harmonic identified ctr" %str(i+1)))
    nl_func = nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)
    return Volterra_ir, nl_func

def nonlinearconvolution_chebyshev_temporalreversal_adaptivefilter(sweep_generator, outputs, branches=5):
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

    # output_sweep = nlsp.append_zeros(output_sweep)
    output_sweep = outputs[0]
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(output_sweep).GetSpectrum()
    out_spec = out_spec / output_sweep.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()

    # Novaks method
    # ir_harmonics_all = nlsp.FindHarmonicImpulseResponse_Novak(ir_sweep,harmonic_order=branches,sweep_generator=sweep_generator)
    # ir_merger = ir_harmonics_all.GetHarmonicImpulseResponse()

    # Jonas method
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(2**12)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)
    for i in range(branches-1):
        split_harm = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=ir_sweep,
                                                            harmonic_order=i+2,
                                                            sweep_generator=sweep_generator).GetHarmonicImpulseResponse()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=split_harm.GetLabels()))
    ir_merger = ir_merger.GetOutput()
    # nlsp.common.plots.plot(ir_merger)
    Volterra_ir = []
    for i in range(len(ir_merger.GetChannels())):
        ir_harmonics =  sumpf.modules.SplitSignal(data=ir_merger, channels=[i]).GetOutput()
        Volterra_ir.append(nlsp.relabel(ir_harmonics,"%r harmonic identified ctr" %str(i+1)))
    nl_func = nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)
    hgm_kernel = []
    for i in range(len(Volterra_ir)):
        kernel = Volterra_ir[i]
        u = nlsp.NonlinearFunction.chebyshev1_polynomial(i+1,sweep_generator.GetOutput())
        u = u.GetOutput().GetChannels()[0]
        d = outputs[i+1].GetChannels()[0]
        M = len(kernel)  # Number of filter taps in adaptive filter
        step = 0.9999  # Step size
        init_coeff = numpy.array(kernel.GetChannels()[0])
        y1, e1, w1 = adaptfilt.nlms(u, d, M, step, returnCoeffs=True, initCoeffs=init_coeff)
        hgm_kernel.append(sumpf.Signal(channels=(w1[-1],),samplingrate=kernel.GetSamplingRate(),labels=kernel.GetLabels()))
    return hgm_kernel, nl_func

