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
    response = output
    variance = sumpf.modules.SignalMean(input_gen.GetOutput() * input_gen.GetOutput()).GetMean()[0] - \
               (sumpf.modules.SignalMean(input_gen.GetOutput()).GetMean()[0]**2)
    kernels = []
    for branch in range(1, branches + 1):
        input = nlsp.NonlinearFunction.hermite_polynomial(branch,excitation)
        cross_corr = sumpf.modules.CorrelateSignals(signal1=input.GetOutput(),signal2=response,
                                                    mode=sumpf.modules.CorrelateSignals.SPECTRUM).GetOutput()
        factor = (math.factorial(branch) * (variance ** branch))
        factor = sumpf.modules.ConstantSignalGenerator(value=factor,samplingrate=cross_corr.GetSamplingRate(),length=len(cross_corr)).GetSignal()
        k = cross_corr * factor
        kernels.append(k)
    kernels[1] = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=excitation.GetSamplingRate(),length=len(cross_corr)).GetSignal()
    kernels[2] = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=excitation.GetSamplingRate(),length=len(cross_corr)).GetSignal()
    nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
    return kernels, nl_func

# sampling_rate = 48000.0
# sweep_start_freq = 20.0
# sweep_stop_freq = 20000.0
# sweep_length = 2 ** 10
# branches = 5
# distribution = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
# iden_method = [nlsp.wgn_hgm_identification]
#
# Plot = True
# Save = False
#
# wgn = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
#                                   stop_frequency=sweep_stop_freq, distribution=distribution)
# prp = sumpf.modules.ChannelDataProperties()
# prp.SetSignal(wgn.GetOutput())
# filt = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=10), transform=True,
#                                      resolution=prp.GetResolution(),frequency=2000.0, length=prp.GetSpectrumLength()).GetSpectrum()
# filt = sumpf.modules.InverseFourierTransform(filt).GetSignal()
# branch = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=wgn.GetOutput(),
#                                                          nonlin_func=nlsp.function_factory.hermite_polynomial(3),
#                                                          max_harm=3, filter_impulseresponse=filt)
# kernel, nl_function = findkernel(wgn, branch.GetOutput(), branches)
# print len(kernel),len(nl_function)
# model = nlsp.HammersteinGroupModel_up(input_signal=wgn.GetOutput(),nonlinear_functions=nl_function, filter_irs=kernel, max_harmonics=range(1,branches+1))
#
# plot.relabelandplotphase(sumpf.modules.FourierTransform(branch.GetOutput()).GetSpectrum(),"Reference System",show=False)
# plot.relabelandplotphase(sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),"NL Identified System",show=True)
