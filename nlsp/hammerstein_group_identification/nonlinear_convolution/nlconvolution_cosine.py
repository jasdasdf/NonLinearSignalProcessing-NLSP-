import nlsp
import sumpf

def nonlinearconvolution_chebyshev_cosine(input_sweep, output_sweep, sweep_start_freq=20.0, sweep_stop_freq=20000.0,
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
                                                               sweep_duration=sweep_length/
                                                               ip_signal.GetSamplingRate()).GetHarmonicImpulseResponse()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ip_signal.GetSamplingRate(), labels=split_harm.GetLabels()))
    harmonics_ir = []
    for i in range(len(ir_merger.GetOutput().GetChannels())):
        ir_harmonics =  sumpf.modules.SplitSignal(data=ir_merger.GetOutput(), channels=[i]).GetOutput()
        harmonics_ir.append(ir_harmonics)
    constant = sumpf.modules.ConstantSignalGenerator(value=1.0,samplingrate=harmonics_ir[1].GetSamplingRate(),length=len(harmonics_ir[1])).GetSignal()
    Volterra_ir = []
    Volterra_ir.append(harmonics_ir[0])
    Volterra_ir.append((1/2.0)*(harmonics_ir[1]+sumpf.modules.AmplifySignal(input=constant,factor=1.0).GetOutput()))
    Volterra_ir.append((1/4.0)*(harmonics_ir[2]+3.0*Volterra_ir[0]))
    Volterra_ir.append((1/8.0)*(harmonics_ir[3]+8.0*Volterra_ir[1]-sumpf.modules.AmplifySignal(input=constant,factor=-1.0).GetOutput()))
    Volterra_ir.append((1/16.0)*(harmonics_ir[4]+20*Volterra_ir[2]-5*Volterra_ir[0]))
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return Volterra_ir, nl_func
