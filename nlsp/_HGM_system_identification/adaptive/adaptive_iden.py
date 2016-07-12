import nlsp
import sumpf
import numpy
import nlsp.common.plots as plot
import adaptfilt as adf

def adaptive_identification(input_generator, outputs, branches=5, iterations=1, step_size=0.1,
                                        filtertaps=2**11, algorithm=nlsp.miso_nlms_multichannel, init_coeffs=None,
                                        Plot_SERvsIteration = False, Print_SER = False,
                                        nonlinear_func = nlsp.function_factory.legrendre_polynomial):
    """
    Adaptive system identification.
    :param input_generator: the input generator object or the input signal
    :param outputs: the response of the system
    :param branches: total number of branches
    :param iterations: total number of iterations
    :param step_size: the step size for adaptive filtering
    :param filtertaps: the total number of filter taps
    :param algorithm: the adaptation algorithm
    :param init_coeffs: initial coefficients
    :param Plot_SERvsIteration: plot ser vs iteration graph
    :param Print_SER: print SER value for each iteration
    :param nonlinear_func: the nonlinear function of the resulting model
    :return: the array of filter kernels and the nonlinear functions
    """
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
    nl_func = nlsp.nl_branches(nonlinear_func,branches)
    return kernel,nl_func