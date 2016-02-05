import sumpf
import nlsp
import common.plot as plot

def nonlinearconvolution_chebyshev_filter(input_sweep, output_sweep, prop):
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
    if prop is None:
        prop = [20.0, 20000.0, 5]
    sweep_start_freq = prop[0]
    sweep_stop_freq = prop[1]
    sweep_length = len(input_sweep)
    branch = prop[2]
    print "chebyshev NL convolution type identification"
    print "sweep_start:%f, stop:%f, length:%f, branch:%d" %(sweep_start_freq,sweep_stop_freq,sweep_length,branch)

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
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=sweep_length/2).GetOutput()
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)

    for i in range(branch-1):
        split_harm = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=ir_sweep,
                                                               harmonic_order=i+2,
                                                               sweep_start_frequency=sweep_start_freq,
                                                               sweep_stop_frequency=sweep_stop_freq,
                                                               sweep_duration=sweep_length/
                                                               ip_signal.GetSamplingRate()).GetHarmonicImpulseResponse()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ip_signal.GetSamplingRate(), labels=split_harm.GetLabels()))
    Volterra_ir = []
    for i in range(len(ir_merger.GetOutput().GetChannels())):
        ir_harmonics =  sumpf.modules.SplitSignal(data=ir_merger.GetOutput(), channels=[i]).GetOutput()
        Volterra_ir.append(ir_harmonics)
    return Volterra_ir

def nonlinearconvolution_chebyshev_nlfunction(branches):
    """
    This function returns the nonlinear function to the nonlinear blocks of the hammerstein group model.
    In nonlinear convolution method the nonlinear function is defined by chebyshev series expansion, Hence it returns
    the chebyshev series expansion functions.
    The chebyshev series expansion is done by using nlsp function factory functions.
    :return: the nonlinear functions to the hammerstein group model
    """
    nl_functions = []
    for i in range(branches):
        nl_functions.append(nlsp.function_factory.chebyshev1_polynomial(i+1))
    return nl_functions