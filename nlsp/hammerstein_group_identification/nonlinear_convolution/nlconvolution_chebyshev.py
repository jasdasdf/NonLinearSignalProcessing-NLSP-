import sumpf
import nlsp
import common.plot as plot

def nonlinearconvolution_chebyshev(input_sweep, output_sweep, sweep_start_freq=20.0, sweep_stop_freq=20000.0,
                                           sweep_length=None,branches=5):
    """
    Function to find the filter impulse response of the hammerstein group model using Chebyshev
    Nonlinear convolution method.
    It is used for nonlinear system identification.
    This function computes the impulse response of the nonlinear system by multiplying the transfer function of the
    output sweep and the regularized spectral inversion of the input sweep. The regularized spectral inversion makes
    sure that the low magnitude frequencies in the input signal is not amplified unanticipatedly due to division in
    frequency domain.
    Then the transfer function is inverse transformed to get the impulse response of the nonlinear system.
    From the nonlinear system impulse response the impulse response of the harmonics are seperated. The higher order
    harmonics impulse response are found in the noncausal part. Since we have calculated the impulse response from the
    frequency domain, it appears in the end of the impulse response due to circular convolution.
    The impulse response of the harmonics are used as the filter impulse response in chebyshev nonlinear convolution
    method.
    The mathematical functions are performed by using the sumpf classes.
    :param input_sweep: the input sweep signal which is given to the nonlinear system
    :param output_sweep: the output signal which is observed from the nonlinear system
    :param prop: a tuple of sweep start frequency, sweep stop frequency and number of branches
    :return: the impulse response of the filters of hammerstein group model
    """
    sweep_start_freq = sweep_start_freq
    sweep_stop_freq = sweep_stop_freq
    if sweep_length is None:
        sweep_length = len(input_sweep)
    else:
        sweep_length = sweep_length
    branch = branches

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
    inversed_ip = sumpf.modules.RegularizedSpectrumInversion(spectrum=ip_spectrum,start_frequency=0,
                                                             stop_frequency=input_sweep.GetSamplingRate()/2).GetOutput()
    tf_sweep = sumpf.modules.MultiplySpectrums(spectrum1=inversed_ip, spectrum2=op_spectrum).GetOutput()
    ir_sweep = sumpf.modules.InverseFourierTransform(spectrum=tf_sweep).GetSignal()
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)

    for i in range(branch-1):
        split_harm = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=ir_sweep,
                                                               harmonic_order=i+2,
                                                               sweep_start_frequency=sweep_start_freq,
                                                               sweep_stop_frequency=sweep_stop_freq,
                                                               sweep_duration=(sweep_length/ip_signal.GetSamplingRate())).GetHarmonicImpulseResponse()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ip_signal.GetSamplingRate(), labels=split_harm.GetLabels()))
    Volterra_ir = []
    for i in range(len(ir_merger.GetOutput().GetChannels())):
        ir_harmonics =  sumpf.modules.SplitSignal(data=ir_merger.GetOutput(), channels=[i]).GetOutput()
        Volterra_ir.append(ir_harmonics)
    nl_func = nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)
    return Volterra_ir, nl_func