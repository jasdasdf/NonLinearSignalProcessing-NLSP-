import nlsp
import sumpf
import numpy

def adaptive_identification(input_generator, outputs, branches=5, nonlinear_func=nlsp.function_factory.power_series, iterations=10, step_size=0.1, filtertaps=1024):

    # impulse = sumpf.modules.ImpulseGenerator(samplingrate=48000.0,length=len(input_generator.GetOutput())).GetSignal()
    # iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_generator.GetOutput(),
    #                                              nonlinear_functions=nlsp.nl_branches(nonlinear_func,branches),
    #                                              filter_irs=[impulse,]*branches,
    #                                              max_harmonics=range(1,branches+1))
    nl_output = nlsp.NonlinearFunction(signal=input_generator.GetOutput())
    input_signal = []
    for i in range(branches):
        nl_output.SetNonlinearFunction(nonlinear_func(i+1))
        input_signal.append(nl_output.GetOutput().GetChannels()[0])
    desired_signal = outputs.GetChannels()[0]
    w = numpy.zeros((len(input_signal),filtertaps))
    for i in range(iterations):
        w = nlsp.multichannel_nlms(input_signal, desired_signal, filtertaps, step_size, initCoeffs=w)
        kernel = []
        for k in w:
            iden_filter = sumpf.Signal(channels=(k,), samplingrate=48000.0, labels=("filter",))
            kernel.append(iden_filter)
        print "iteration %r" %(i+1)
        # iden_nlsystem.SetFilterIRS(kernel)
        # print "SNR %r,iteration %r" %(nlsp.snr(outputs,iden_nlsystem.GetOutput()),i+1)
    nl_func = nlsp.nl_branches(nonlinear_func,branches)
    return kernel,nl_func
