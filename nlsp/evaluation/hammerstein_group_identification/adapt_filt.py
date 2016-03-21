import numpy as np
import matplotlib.pyplot as plt
import adaptfilt as adf
import sumpf
import nlsp
import nlsp.common.plots as plot

branches = 1
input = nlsp.NovakSweepGenerator_Sine(sampling_rate=48000.0,length=2**15,start_frequency=20.0,stop_frequency=20000.0)
# input = nlsp.WhiteGaussianGenerator()
impulse = sumpf.modules.ImpulseGenerator(samplingrate=48000.0,length=len(input.GetOutput())).GetSignal()
prop = sumpf.modules.ChannelDataProperties()
prop.SetSignal(impulse)
# fil = nlsp.create_bpfilter([9000],input.GetOutput())
# ref_nlsystem = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input.GetOutput(),nonlin_func=nlsp.function_factory.power_series(2),max_harm=2,
#                                                 filter_impulseresponse=fil[0],downsampling_position=1)
fil = nlsp.log_bpfilter(branches=branches,input=input.GetOutput())
ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input.GetOutput(),
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.legrendre_polynomial,branches),
                                                 filter_irs=fil,
                                                 max_harmonics=range(1,branches+1))
iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input.GetOutput(),
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.legrendre_polynomial,branches),
                                                 filter_irs=[impulse,]*branches,
                                                 max_harmonics=range(1,branches+1))

input_signal = []
for i in range(branches):
    inp = ref_nlsystem.GetHammersteinBranchNLOutput(i+1)
    input_signal.append(inp.GetChannels()[0])

desired_signal = ref_nlsystem.GetOutput().GetChannels()[0]
filtertaps = 1024
step = 0.1
iterations = 1000
w = np.zeros((len(input_signal),filtertaps))
error = []
for i in range(iterations):
    w = nlsp.multichannel_nlms(input_signal, desired_signal, filtertaps, step, initCoeffs=w)
    kernel = []
    for k in w:
        iden_filter = sumpf.Signal(channels=(k,), samplingrate=48000.0, labels=("filter",))
        kernel.append(iden_filter)
    iden_nlsystem.SetFilterIRS(kernel)
    print "SNR %r" %nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem.GetOutput())

plot.relabelandplot(iden_nlsystem.GetOutput(),"identified",show=False)
plot.relabelandplot(ref_nlsystem.GetOutput(),"reference",show=True)
for i in range(len(fil)):
    plot.relabelandplot(sumpf.modules.FourierTransform(fil[i]).GetSpectrum(),"Ref filter",show=False)
    plot.relabelandplot(sumpf.modules.FourierTransform(kernel[i]).GetSpectrum(),"Iden filter",show=False)
plot.show()
