import math
import sumpf
import nlsp


def wiener_g_identification(input_gen, output, branches):
    """
    System identification using Wiener G functionals.
    :param input_gen: the input generator or the input signal
    :param output: the response of the nonlinear system
    :param branches: the total number of branches
    :return: the filter kernels and the nonlinear functions
    """
    kernel_length = len(output)/2
    if hasattr(input_gen,"GetOutput"):
        excitation = input_gen.GetOutput()
    else:
        excitation = input_gen
    response = output
    variance = sumpf.modules.SignalMean(input_gen.GetOutput() * input_gen.GetOutput()).GetMean()[0]
    kernels = []
    for branch in range(1, branches + 1):
        k = []
        for i in range(0, kernel_length):
            shifted = sumpf.modules.ShiftSignal(signal=excitation, shift=-i,circular=False).GetOutput()
            power = nlsp.NonlinearFunction(signal=shifted,nonlin_func=nlsp.function_factory.hermite_polynomial(branch))
            product = response * power.GetOutput()
            mean = sumpf.modules.SignalMean(signal=product).GetMean()[0]
            factor = 1.0 / (math.factorial(branch) * (variance ** branch))
            k.append(mean * factor)
        k = sumpf.Signal(channels=(k,),samplingrate=output.GetSamplingRate(),labels=())
        kernels.append(k)
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return kernels, nl_func
