import numpy as np
import matplotlib.pyplot as plt
import adaptfilt as adf
import sumpf
import nlsp
import nlsp.common.plots as plot

branches = 2
input = nlsp.NovakSweepGenerator_Sine(sampling_rate=48000.0,length=2**15,start_frequency=20.0,stop_frequency=20000.0)
# input = nlsp.WhiteGaussianGenerator()
impulse = sumpf.modules.ImpulseGenerator(samplingrate=48000.0,length=len(input.GetOutput())).GetSignal()
prop = sumpf.modules.ChannelDataProperties()
prop.SetSignal(impulse)
fil = nlsp.create_bpfilter([9000],input.GetOutput())
ref_nlsystem = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input.GetOutput(),nonlin_func=nlsp.function_factory.power_series(3),max_harm=3,
                                                filter_impulseresponse=fil[0],downsampling_position=1)
# fil = nlsp.log_bpfilter(branches=branches,input=input.GetOutput())
# ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input.GetOutput(),
#                                                  nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.laguerre_polynomial,branches),
#                                                  filter_irs=fil,
#                                                  max_harmonics=range(1,branches+1))

input_signal = ref_nlsystem.GetNLOutput().GetChannels()[0]
print len(input_signal)
desired_signal = ref_nlsystem.GetOutput().GetChannels()[0]
print len(desired_signal)
filtertaps = 1024
step = 0.1
iterations = 25
kernel = np.zeros(filtertaps)
for i in range(iterations):
    y, e, w = adf.nlms(input_signal, desired_signal, filtertaps, step, returnCoeffs=False,initCoeffs=kernel)
    kernel = w
    print np.sum(e)

iden_filter = sumpf.Signal(channels=(kernel,), samplingrate=48000.0, labels=("filter",))
print len(iden_filter)
iden_nlsystem = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input.GetOutput(),nonlin_func=nlsp.function_factory.power_series(3),max_harm=3,
                                                filter_impulseresponse=iden_filter)

plot.relabelandplot(iden_nlsystem.GetOutput(),"identified",show=False)
plot.relabelandplot(ref_nlsystem.GetOutput(),"reference",show=True)
plot.relabelandplot(sumpf.modules.FourierTransform(fil[0]).GetSpectrum(),"Ref filter",show=False)
plot.relabelandplot(sumpf.modules.FourierTransform(iden_filter).GetSpectrum(),"Iden filter",show=True)
print nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem.GetOutput())
