import sumpf
import nlsp
import nlsp.common.plots as plot

branches = 3
sampling_rate = 48000.0
length = 2**18
start_freq = 100.0
stop_freq = 20000.0
fade_out = 0.00
fade_in = 0.00

# normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()

sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
# cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
#                                    stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
# wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
#                                    stop_frequency=stop_freq, distribution=normal)
# wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
#                                    stop_frequency=stop_freq, distribution=uniform)
noise = sumpf.modules.NoiseGenerator(distribution=uniform, samplingrate=sampling_rate, length=length)
input_generator = noise
nl_f = nlsp.function_factory.power_series

# virtual reference system
# input = input_generator.GetSignal()
# # fil = nlsp.create_bpfilter([3000,10000,20000],input)
# # fil = [i for i in reversed(fil)]
# fil = nlsp.log_bpfilter(start_freq,stop_freq,branches,input)
# ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input,
#                                                  nonlinear_functions=nlsp.nl_branches(nl_f,branches),
#                                                  filter_irs=fil,
#                                                  max_harmonics=range(1,branches+1))
# output = ref_nlsystem.GetOutput()

# real world reference system
load = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/Noise18.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
load_sweep = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sine.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
output = sumpf.modules.SplitSignal(data=load.GetSignal(),channels=[1]).GetOutput()
input = sumpf.modules.SplitSignal(data=load.GetSignal(),channels=[0]).GetOutput()



found_filter_spec, nl_functions = nlsp.adaptive_identification(input,output,branches,nl_f,iterations=1,
                                                               step_size=0.1,filtertaps=2**10,algorithm=nlsp.multichannel_nlms,Plot=False)
iden_nlsystem= nlsp.HammersteinGroupModel_up(input_signal=input,
                                             nonlinear_functions=nl_functions,
                                             filter_irs=found_filter_spec,
                                             max_harmonics=range(1,branches+1))

# plot.plot_filterspec(found_filter_spec,show=False)
# plot.plot_filterspec(fil,show=True)
plot.relabelandplotphase(sumpf.modules.FourierTransform(output).GetSpectrum(),"Reference System",show=False)
plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
print "SNR between Reference and Identified output with reversed filter orders: %r" %nlsp.snr(output,
                                                                                                 iden_nlsystem.GetOutput())


