import sumpf
import nlsp
import nlsp.common.plots as plot

def filterkernel_evaluation(reference_kernels, identified_kernels, Plot=False):
    identified_kernels = nlsp.change_length_filterkernels(identified_kernels,len(reference_kernels[0]))
    for i,(reference_kernel, identified_kernel) in enumerate(zip(reference_kernels,identified_kernels)):
        sub = identified_kernel - reference_kernel
        sub = sumpf.modules.FourierTransform(sub).GetSpectrum()
        print nlsp.calculateenergy_freq(sub),i
        print
        plot.relabelandplot(sub,"kernel %d difference" %(i+1),show=False)
    plot.show()


def powerserieshgm_uniqueness_evaluation():
    for method,input_generator,label in zip(iden_method,excitation,labels):
        input_signal = input_generator.GetOutput()
        filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        found_filter_spec, nl_functions = method(input_generator,ref_nlsystem.GetOutput(),branches)
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        filterkernel_evaluation(filter_spec_tofind,found_filter_spec)
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
        print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput(),label=label)

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**15
fade_out = 0.00
fade_in = 0.00
branches = 3
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()

Plot = False
Save = False

sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)
excitation = [sine,
              cos,
              wgn_normal,
              wgn_uniform,
              wgn_normal]
iden_method = [nlsp.nonlinearconvolution_powerseries_temporalreversal,
               nlsp.nonlinearconvolution_chebyshev_temporalreversal,
               nlsp.miso_identification,
               nlsp.wiener_g_identification_corr,
               nlsp.adaptive_identification]
labels = ["NL_powerseries","NL_chebyshev","MISO","WienerG","adaptive"]
powerserieshgm_uniqueness_evaluation()