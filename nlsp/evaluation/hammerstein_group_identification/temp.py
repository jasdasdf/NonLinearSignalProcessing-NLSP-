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
# uniform = sumpf.modules.NoiseGenerator.UniformDistribution()

sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
# cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
#                                    stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
# wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
#                                    stop_frequency=stop_freq, distribution=normal)
# wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
#                                    stop_frequency=stop_freq, distribution=uniform)

input_generator = sine_g
nl_f = nlsp.function_factory.power_series

input = input_generator.GetOutput()
fil = nlsp.create_bpfilter([3000,8000,20000],input)
fil = [i for i in reversed(fil)]
ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input,
                                                 nonlinear_functions=nlsp.nl_branches(nl_f,branches),
                                                 filter_irs=fil,
                                                 max_harmonics=range(1,branches+1))
output = ref_nlsystem.GetOutput()

found_filter_spec, nl_functions = nlsp.adaptive_identification(input_generator,output,branches,nl_f,iterations=5,
                                                               step_size=0.02,filtertaps=2**10,algorithm=nlsp.multichannel_nlms,Plot=False)
iden_nlsystem= nlsp.HammersteinGroupModel_up(input_signal=input,
                                             nonlinear_functions=nl_functions,
                                             filter_irs=found_filter_spec,
                                             max_harmonics=range(1,branches+1))

plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
print "SNR between Reference and Identified output with reversed filter orders: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput())


