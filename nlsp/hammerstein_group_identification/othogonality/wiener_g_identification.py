import math
import sumpf
import nlsp


def wiener_g_identification(input_gen, output, branches):
    kernel_length = len(output)/2
    excitation = input_gen.GetOutput()
    response = output
    variance = sumpf.modules.SignalMean(input_gen.GetOutput() * input_gen.GetOutput()).GetMean()[0]
    kernels = []
    for branch in range(1, branches + 1):
        k = []
        for i in range(0, kernel_length):
            shifted = sumpf.modules.ShiftSignal(signal=excitation,shift=-i,circular=False).GetOutput()
            power = nlsp.NonlinearFunction(signal=shifted,nonlin_func=nlsp.function_factory.hermite_polynomial(branch))
            product = response * power.GetOutput()
            mean = sumpf.modules.SignalMean(signal=product).GetMean()[0]
            factor = 1.0 / (math.factorial(branch) * (variance ** branch))
            k.append(mean * factor)
        k = sumpf.Signal(channels=(k,),samplingrate=output.GetSamplingRate(),labels=())
        kernels.append(k)
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return kernels, nl_func

def wiener_g_identification_corr(input_gen, output, branches):
    excitation = input_gen.GetOutput()
    mean = sumpf.modules.ConstantSignalGenerator(value=nlsp.get_mean(excitation)[0], samplingrate=excitation.GetSamplingRate(),
                                          length=len(excitation)).GetSignal()
    excitation = excitation - mean
    response = output
    variance = sumpf.modules.SignalMean(excitation * excitation).GetMean()[0]
    kernels = []
    for branch in range(1, branches + 1):
        input = nlsp.NonlinearFunction.power_series(branch,excitation)
        cross_corr = sumpf.modules.CorrelateSignals(signal1=input.GetOutput(),signal2=response,
                                                    mode=sumpf.modules.CorrelateSignals.SPECTRUM).GetOutput()
        factor = 1.0 / (math.factorial(branch) * (variance ** branch))
        factor = sumpf.modules.ConstantSignalGenerator(value=factor,samplingrate=cross_corr.GetSamplingRate(),length=len(cross_corr)).GetSignal()
        k = cross_corr * factor
        kernels.append(k)
    nl_func = nlsp.nl_branches(nlsp.function_factory.hermite_polynomial,branches)
    return kernels, nl_func
