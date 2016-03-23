import nlsp
import sumpf
import numpy

def adaptive_identification(input_generator, outputs, branches=5, nonlinear_func=nlsp.function_factory.power_series, iterations=10, step_size=0.1, filtertaps=1024,
                            algorithm=nlsp.multichannel_ap):

    if hasattr(input_generator,"GetOutput"):
        input = input_generator.GetOutput()
    else:
        input = input_generator
    impulse = sumpf.modules.ImpulseGenerator(samplingrate=48000.0,length=len(input)).GetSignal()
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input,
                                                 nonlinear_functions=nlsp.nl_branches(nonlinear_func,branches),
                                                 filter_irs=[impulse,]*branches,
                                                 max_harmonics=range(1,branches+1))
    input_signal = []
    nl = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input)
    for i in range(branches):
        nl.SetNLFunction(nonlinear_func(i))
        input_signal.append(nl.GetOutput().GetChannels()[0])
    desired_signal = outputs.GetChannels()[0]
    w = numpy.zeros((len(input_signal),filtertaps))
    for i in range(iterations):
        w = algorithm(input_signal, desired_signal, filtertaps, step_size, initCoeffs=w)
        kernel = []
        for k in w:
            iden_filter = sumpf.Signal(channels=(k,), samplingrate=48000.0, labels=("filter",))
            kernel.append(iden_filter)
        print "iteration %r" %(i+1)
        iden_nlsystem.SetFilterIRS(kernel)
        print "SNR %r,iteration %r" %(nlsp.snr(outputs,iden_nlsystem.GetOutput()),i+1)
    nl_func = nlsp.nl_branches(nonlinear_func,branches)
    return kernel,nl_func
