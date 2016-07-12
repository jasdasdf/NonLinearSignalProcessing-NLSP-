import sumpf
import nlsp
import numpy
import math
import common.plot as plot

def sine_sweepbased_spectralinversion(sweep_generator, output_sweep, branches=5):
    """
    Sweep-based system identification using spectral inversion technique and using sine sweep signal.
    :param sweep_generator: the sweep generator object
    :param output_sweep: the output sweep of the nonlinear system
    :param branches: the total number of output branches
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
    inversed_ip = sumpf.modules.RegularizedSpectrumInversion(spectrum=ip_spectrum,start_frequency=sweep_start_freq+50,
                                                             stop_frequency=sweep_stop_freq-100).GetOutput()
    tf_sweep = sumpf.modules.MultiplySpectrums(spectrum1=inversed_ip, spectrum2=op_spectrum).GetOutput()
    ir_sweep = sumpf.modules.InverseFourierTransform(spectrum=tf_sweep).GetSignal()
    # nlsp.common.plots.plot(ir_sweep)
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

    tf_harmonics_all = sumpf.modules.FourierTransform(signal=ir_merger).GetSpectrum()
    harmonics_tf = []
    for i in range(len(tf_harmonics_all.GetChannels())):
        tf_harmonics =  sumpf.modules.SplitSpectrum(data=tf_harmonics_all, channels=[i]).GetOutput()
        harmonics_tf.append(tf_harmonics)
    A_matrix = numpy.zeros((branches,branches),dtype=numpy.complex128)
    for n in range(0,branches):
        for m in range(0,branches):
            if ((n >=m) and ((n+m) % 2 == 0)):
                A_matrix[m][n] = (((-1 + 0j)**(2*(n+1)-m/2))/(2**n)) * nlsp.binomial((n+1),(n-m)/2)
            else:
                A_matrix[m][n] = 0
    A_inverse = numpy.linalg.inv(A_matrix)
    for row in range(0,len(A_inverse)):
        if row % 2 != 0.0:
            A_inverse[row] = A_inverse[row] * (0+1j)
    B = []
    for row in range(0,branches):
        A = sumpf.modules.ConstantSpectrumGenerator(value=0.0,resolution=harmonics_tf[0].GetResolution(),
                                                    length=len(harmonics_tf[0])).GetSpectrum()
        for column in range(0,branches):
            temp = sumpf.modules.AmplifySpectrum(input=harmonics_tf[column],factor=A_inverse[row][column]).GetOutput()
            A = A + temp
        B_temp = nlsp.relabel(sumpf.modules.InverseFourierTransform(A).GetSignal(),"%r harmonic identified psi" %str(row+1))
        B.append(B_temp)
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return B,nl_func


def sine_sweepbased_temporalreversal(sweep_generator, output_sweep, branches=5):
    """
    Sweep-based system identification using temporal reversal technique and using sine sweep signal.
    :param sweep_generator: the sweep generator object
    :param output_sweep: the output sweep of the nonlinear system
    :param branches: the total number of output branches
    :return: the parameters of HGM (filter kernels and nonlinear functions)
    """
    sweep_length = sweep_generator.GetLength()
    # output_sweep = nlsp.append_zeros(output_sweep)
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(output_sweep).GetSpectrum()
    out_spec = out_spec / output_sweep.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()
    # nlsp.common.plots.plot(ir_sweep)
    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)
    for i in range(branches-1):
        split_harm = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=ir_sweep,
                                                            harmonic_order=i+2,
                                                            sweep_generator=sweep_generator).GetHarmonicImpulseResponse()
        split_harm = sumpf.modules.CutSignal(signal=split_harm,stop=len(sweep_generator.GetOutput())).GetOutput()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=split_harm.GetLabels()))
    ir_merger = ir_merger.GetOutput()
    # nlsp.common.plots.plot(ir_merger)
    tf_harmonics_all = sumpf.modules.FourierTransform(ir_merger).GetSpectrum()
    harmonics_tf = []
    for i in range(len(tf_harmonics_all.GetChannels())):
        tf_harmonics =  sumpf.modules.SplitSpectrum(data=tf_harmonics_all, channels=[i]).GetOutput()
        harmonics_tf.append(tf_harmonics)
    A_matrix = numpy.zeros((branches,branches),dtype=numpy.complex128)
    for n in range(0,branches):
        for m in range(0,branches):
            if ((n >=m) and ((n+m) % 2 == 0)):
                A_matrix[m][n] = (((-1 + 0j)**(2*(n+1)-m/2))/(2**n)) * nlsp.binomial((n+1),(n-m)/2)
            else:
                A_matrix[m][n] = 0
    A_inverse = numpy.linalg.inv(A_matrix)
    for row in range(0,len(A_inverse)):
        if row % 2 != 0.0:
            A_inverse[row] = A_inverse[row] * (0+1j)
    B = []
    for row in range(0,branches):
        A = sumpf.modules.ConstantSpectrumGenerator(value=0.0,resolution=harmonics_tf[0].GetResolution(),
                                                    length=len(harmonics_tf[0])).GetSpectrum()
        for column in range(0,branches):
            temp = sumpf.modules.AmplifySpectrum(input=harmonics_tf[column],factor=A_inverse[row][column]).GetOutput()
            A = A + temp
        B_temp = nlsp.relabel(sumpf.modules.InverseFourierTransform(A).GetSignal(),"%r harmonic identified ptr" %str(row+1))
        B.append(B_temp)
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return B,nl_func



