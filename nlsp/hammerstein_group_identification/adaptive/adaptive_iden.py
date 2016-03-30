import nlsp
import sumpf
import numpy
import nlsp.common.plots as plot
import adaptfilt as adf

def adaptive_identification(input_generator, outputs, branches=5, nonlinear_func=nlsp.function_factory.power_series, iterations=100, step_size=0.0035, filtertaps=1024,
                            algorithm=nlsp.multichannel_nlms_ideal, init_coeffs=None):

    if hasattr(input_generator,"GetOutput"):
        input = input_generator.GetOutput()
    else:
        input = input_generator
    impulse = sumpf.modules.ImpulseGenerator(samplingrate=outputs.GetSamplingRate(),length=len(input)).GetSignal()
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input,
                                                 nonlinear_functions=nlsp.nl_branches(nonlinear_func,branches),
                                                 filter_irs=[impulse,]*branches,
                                                 max_harmonics=range(1,branches+1))
    input_signal = []
    for i in range(branches):
        input_signal.append(iden_nlsystem.GetHammersteinBranchNLOutput(i+1).GetChannels()[0])
    desired_signal = outputs.GetChannels()[0]
    if init_coeffs is None:
        w = numpy.zeros((len(input_signal),filtertaps))
    else:
        w = []
        for k in init_coeffs:
            w.append(numpy.asarray(k.GetChannels()[0]))
    for i in range(iterations):
        w = algorithm(input_signal, desired_signal, filtertaps, step_size, initCoeffs=w)
        kernel = []
        for k in w:
            iden_filter = sumpf.Signal(channels=(k,), samplingrate=outputs.GetSamplingRate(), labels=("filter",))
            kernel.append(iden_filter)
        iden_nlsystem.SetFilterIRS(kernel)
        print "SNR %r,iteration %r" %(nlsp.snr(outputs,iden_nlsystem.GetOutput()),i+1)
    nl_func = nlsp.nl_branches(nonlinear_func,branches)
    return kernel,nl_func
