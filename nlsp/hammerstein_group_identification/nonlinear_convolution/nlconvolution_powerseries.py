import sumpf
import nlsp
import common.plot as plot

def nonlinearconvolution_powerseries(input_sweep, output_sweep, sweep_start_freq=20.0, sweep_stop_freq=20000.0,
                                           sweep_length=None,branches=5):
    """
    Function to find the filter impulse response of the hammerstein group model using Nonlinear convolution method.
    It is used for nonlinear system identification.
    This function computes the impulse response of the nonlinear system by multiplying the transfer function of the
    output sweep and the regularized spectral inversion of the input sweep. The regularized spectral inversion makes
    sure that the low magnitude frequencies in the input signal is not amplified unanticipatedly due to division in
    frequency domain.
    Then the transfer function is inverse transformed to get the impulse response of the nonlinear system.
    From the nonlinear system impulse response the impulse response of the harmonics are seperated. The higher order
    harmonics impulse response are found in the noncausal part. Since we have calculated the impulse response from the
    frequency domain, it appears in the end of the impulse response due to circular convolution.
    Then the transfer function of the harmonics impulse response is calculated and the mathematical calculation which is
    specified by Farina in Nonlinear convolution paper is performed to find the transfer function of filters which shall
    be used in hammerstein group model. Then it is transformed to time domain and returned.
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
    inversed_ip = sumpf.modules.RegularizedSpectrumInversion(spectrum=ip_spectrum,start_frequency=sweep_start_freq,
                                                             stop_frequency=sweep_stop_freq).GetOutput()
    tf_sweep = sumpf.modules.MultiplySpectrums(spectrum1=inversed_ip, spectrum2=op_spectrum).GetOutput()
    ir_sweep = sumpf.modules.InverseFourierTransform(spectrum=tf_sweep).GetSignal()
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=300).GetOutput()
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
    tf_harmonics_all = sumpf.modules.FourierTransform(signal=ir_merger.GetOutput()).GetSpectrum()
    harmonics_tf = []
    for i in range(len(tf_harmonics_all.GetChannels())):
        tf_harmonics =  sumpf.modules.SplitSpectrum(data=tf_harmonics_all, channels=[i]).GetOutput()
        harmonics_tf.append(tf_harmonics)
    if len(harmonics_tf) != 5:
            harmonics_tf.extend([sumpf.modules.ConstantSpectrumGenerator(value=0.0,
                                                                                  resolution=harmonics_tf[0].GetResolution(),
                                                                                  length=len(harmonics_tf[0])).GetSpectrum()]*(5-len(harmonics_tf)))
    Volterra_tf = []
    Volterra_tf.append(harmonics_tf[0] + (3.0)*harmonics_tf[2] +(5.0)*harmonics_tf[4])
    Volterra_tf.append(sumpf.modules.AmplifySpectrum(input=harmonics_tf[1],factor=2j).GetOutput() +
             sumpf.modules.AmplifySpectrum(input=harmonics_tf[3],factor=8j).GetOutput())
    Volterra_tf.append(-4.0*harmonics_tf[2] - 20.0*harmonics_tf[4])
    Volterra_tf.append(sumpf.modules.AmplifySpectrum(input=harmonics_tf[3],factor=-8j).GetOutput())
    Volterra_tf.append(16.0*harmonics_tf[4])
    Volterra_ir = []
    for kernel in Volterra_tf:
        ift = sumpf.modules.InverseFourierTransform(spectrum=kernel).GetSignal()
        Volterra_ir.append(ift)
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return Volterra_ir[:branches],nl_func

def nonlinearconvolution_powerseries_debug(input_sweep, output_sweep, sweep_start_freq=20.0, sweep_stop_freq=20000.0,
                                           sweep_length=None,branches=5):
    """
    Fuction for debugging purpose
    :param input_sweep: the input sweep signal which is given to the nonlinear system
    :param output_sweep: the output signal which is observed from the nonlinear system
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
    inversed_ip = sumpf.modules.RegularizedSpectrumInversion(spectrum=ip_spectrum,start_frequency=sweep_start_freq,
                                                             stop_frequency=sweep_stop_freq).GetOutput()
    tf_sweep = sumpf.modules.MultiplySpectrums(spectrum1=inversed_ip, spectrum2=op_spectrum).GetOutput()
    ir_sweep = sumpf.modules.InverseFourierTransform(spectrum=tf_sweep).GetSignal()
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=300).GetOutput()
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
    tf_harmonics_all = sumpf.modules.FourierTransform(signal=ir_merger.GetOutput()).GetSpectrum()
    harmonics_tf = []
    for i in range(len(tf_harmonics_all.GetChannels())):
        tf_harmonics =  sumpf.modules.SplitSpectrum(data=tf_harmonics_all, channels=[i]).GetOutput()
        harmonics_tf.append(tf_harmonics)
    Volterra_tf = []
    Volterra_tf.append(harmonics_tf[0] + (3/4.0)*harmonics_tf[2] +(5/8.0)*harmonics_tf[4])
    Volterra_tf.append(sumpf.modules.AmplifySpectrum(input=harmonics_tf[1],factor=-1j/2.0).GetOutput() +
             sumpf.modules.AmplifySpectrum(input=harmonics_tf[3],factor=-1j/2.0).GetOutput())
    Volterra_tf.append((-1/4.0)*harmonics_tf[2] - (5/16.0)*harmonics_tf[4])
    Volterra_tf.append(sumpf.modules.AmplifySpectrum(input=harmonics_tf[3],factor=(1j/8.0)).GetOutput())
    Volterra_tf.append((1/16.0)*harmonics_tf[4])
    Volterra_ir = []
    for kernel in Volterra_tf:
        ift = sumpf.modules.InverseFourierTransform(spectrum=kernel).GetSignal()
        Volterra_ir.append(ift)
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return Volterra_ir[:branches],nl_func