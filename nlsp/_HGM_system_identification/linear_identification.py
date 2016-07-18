import sumpf
import nlsp

def linear_identification_temporalreversal(sweep_generator, output_sweep, branches, length_ir=2**12):
    """
    Linear identification of a system using temporal reversal method.
    :param sweep_generator: the sweep generator object
    :param output_sweep: the output sweep of the nonlinear system
    :return: the filter kernels and the nonlinear functions of the HGM
    """
    srate = output_sweep.GetSamplingRate()
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(output_sweep).GetSpectrum()
    out_spec = out_spec / output_sweep.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()
    ir_sweep = sumpf.modules.CutSignal(signal=ir_sweep, start=0, stop=length_ir).GetOutput()
    ir_sweep = [ir_sweep,]
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    for i in range(1,branches):
        ir_sweep.append(sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=srate,length=length_ir).GetSignal())
    return ir_sweep,nl_func

def linear_identification(sweep_generator, output_sweep, branches, length_ir=2**12):
    """
    Linear identification of a system using reversed sweep method.
    :param sweep_generator: the sweep generator object
    :param output_sweep: the output of the system for sweep input
    :param branches: number of branches
    :param length_ir: length of the impulse response
    :return: the filter kernels and the nonlinear functions of the HGM
    """
    srate = output_sweep.GetSamplingRate()
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(output_sweep).GetSpectrum()
    out_spec = out_spec / output_sweep.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()
    ir_sweep = sumpf.modules.CutSignal(signal=ir_sweep, start=0, stop=length_ir).GetOutput()
    length = len(ir_sweep)
    ir_sweep = [ir_sweep,]
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    for i in range(1,branches):
        ir_sweep.append(sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=srate,length=length).GetSignal())
    return ir_sweep,nl_func

def linear_identification_powerhgm(sweep_generator, output_sweep, branches):
    """
    Linear identification of a system using HGM using sweep signal.
    :param sweep_generator: the sweep generator object
    :param output_sweep: the output of the system for sweep input
    :param branches: number of branches
    :return: the filter kernels and the nonlinear functions of the HGM
    """
    srate = output_sweep.GetSamplingRate()
    filter_kernels, nl_func = nlsp.sine_sweepbased_temporalreversal(sweep_generator,output_sweep,branches)
    ir_sweep = []
    ir_sweep.append(filter_kernels[0])
    length = len(filter_kernels[0])
    for i in range(1,branches):
        ir_sweep.append(sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=srate,length=length).GetSignal())
    return ir_sweep,nl_func