import nlsp
import sumpf
import numpy

def clipping_adaptive_identification(input_generator, outputs, branches=5, iterations=1, step_size=0.1,
                                        filtertaps=2**11, algorithm=nlsp.miso_nlms_multichannel, init_coeffs=None,
                                        Plot_SERvsIteration = False, Print_SER = False,
                                        nonlinear_func = nlsp.function_factory.hardclip):
    clipping_thresholds = ([-1.1,1.1],[-1.0,1.0],[-0.9,0.9],[-0.8,0.8],[-0.7,0.7])
    if hasattr(input_generator,"GetOutput"):
        input = input_generator.GetOutput()
    else:
        input = input_generator
    impulse = sumpf.modules.ImpulseGenerator(samplingrate=outputs.GetSamplingRate(),length=len(input)).GetSignal()
    nl = []
    for th in clipping_thresholds:
        nl.append(nonlinear_func(th))
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input,
                                                 nonlinear_functions=nl,
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
    error_energy = numpy.zeros(iterations)
    SNR = numpy.zeros(iterations)
    iteration = numpy.zeros(iterations)
    for i in range(iterations):
        w = algorithm(input_signal, desired_signal, filtertaps, step_size, initCoeffs=w, plot=Plot_SERvsIteration)
        kernel = []
        for k in w:
            iden_filter = sumpf.Signal(channels=(k,), samplingrate=outputs.GetSamplingRate(), labels=("filter",))
            kernel.append(iden_filter)
        iden_nlsystem.SetFilterIRS(kernel)
        error = sumpf.modules.SubtractSignals(signal1=outputs,signal2=iden_nlsystem.GetOutput()).GetOutput()
        SNR[i] = nlsp.snr(outputs,iden_nlsystem.GetOutput())[0]
        error_energy[i] = nlsp.calculateenergy_time(error)[0]
        iteration[i] = (i+1)*(len(input)-filtertaps+1)
        if Print_SER is True:
            print "SNR          %r, iteration %r" %(SNR[i],iteration[i])
            print "Error energy %r, iteration %r" %(error_energy[i],iteration[i])
            print
    nl_func = nl
    return kernel,nl_func