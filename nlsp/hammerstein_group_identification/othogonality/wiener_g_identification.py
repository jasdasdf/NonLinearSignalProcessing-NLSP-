import sumpf
import nlsp
import nlsp.common.plots as plot

def findkernel(input,output):
    plot.plot(sumpf.modules.CorrelateSignals(signal1=input,signal2=output).GetOutput())



sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
sweep_length = 2**10
branches = 5
distribution = sumpf.modules.NoiseGenerator.WhiteNoise()
iden_method = [nlsp.wgn_hgm_identification]

Plot = True
Save = False

wgn = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, distribution=distribution)
prp = sumpf.modules.ChannelDataProperties()
prp.SetSignal(wgn.GetOutput())
filt = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=10),transform=True,resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
filt = sumpf.modules.InverseFourierTransform(filt).GetSignal()
branch = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=wgn.GetOutput(),nonlin_func=nlsp.function_factory.legrendre_polynomial(3),
                                                         max_harm=3,filter_impulseresponse=filt)
findkernel(wgn.GetOutput(),branch.GetOutput())