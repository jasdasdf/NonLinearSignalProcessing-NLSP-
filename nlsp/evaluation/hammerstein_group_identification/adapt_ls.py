import numpy as np
import matplotlib.pyplot as plt
import adaptfilt as adf
import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000.0
start_freq = 100.0
stop_freq = 20000.0
length = 2**18
fade_out = 0.00
fade_in = 0.00
branches = 5
sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                               stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
op_sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sine.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
op_sine = sumpf.modules.SplitSignal(data=op_sine.GetSignal(),channels=[1]).GetOutput()

kernel = nlsp.linear_identification_kernel(sine,op_sine)
init_coeff = kernel.GetChannels()[0]
M = len(kernel)  # Number of filter taps in adaptive filter
step = 0.9999  # Step size
u = sine.GetOutput().GetChannels()[0]
d = op_sine.GetChannels()[0]
y1, e1, w1 = adf.nlms(u, d, M, step, returnCoeffs=True, initCoeffs=np.array(init_coeff))
filter_iden_hgm = sumpf.Signal(channels=(w1[-1],), samplingrate=48000.0, labels=("filter_hm",))

iden_hgm = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=sine.GetOutput(),nonlin_func=nlsp.function_factory.power_series(1),
                                                           max_harm=1,filter_impulseresponse=filter_iden_hgm)

plot.plot(sumpf.modules.FourierTransform(iden_hgm.GetOutput()).GetSpectrum(),show=False)
plot.plot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),show=True)