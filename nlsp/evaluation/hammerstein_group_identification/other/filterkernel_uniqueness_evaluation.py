import numpy
import itertools
import sumpf
import nlsp
import nlsp.common.plots as plot

# Applicable to only virtual nonlinear system
# Find Uniqueness between reference and identified nonlinear system

def uniqueness_evaluation_allexceptadaptive():
    for method,input_generator,label in zip(iden_method,excitation,labels):
        print method,input_generator
        for nlfunc in nl_functions_all:
            print nlfunc
            input_signal = input_generator.GetOutput()
            filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
            ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                         nonlinear_functions=nlsp.nl_branches(nlfunc,branches),
                                                         filter_irs=filter_spec_tofind,
                                                         max_harmonics=range(1,branches+1))
            found_filter_spec, nl_functions = method(input_generator,ref_nlsystem.GetOutput(),branches)
            iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                         nonlinear_functions=nl_functions,
                                                         filter_irs=found_filter_spec,
                                                         max_harmonics=range(1,branches+1))
            nlsp.filterkernel_evaluation_sum(filter_spec_tofind,found_filter_spec)
            nlsp.filterkernel_evaluation_plot(filter_spec_tofind,found_filter_spec)
            if Plot is True:
                plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
                plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
            print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput(),label=label)
            print
        print
        print

def uniqueness_evaluation_adaptive():
    for input_generator in excitation:
        print "adaptive identification"
        print input_generator
        for nlfunc_ref, nlfunc_iden in itertools.product(nl_functions_all,nl_functions_all):
            print "ref nl function %r" %nlfunc_ref
            print "iden nl function %r" %nlfunc_iden
            input_signal = input_generator.GetOutput()
            filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
            ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                         nonlinear_functions=nlsp.nl_branches(nlfunc_ref,branches),
                                                         filter_irs=filter_spec_tofind,
                                                         max_harmonics=range(1,branches+1))
            found_filter_spec, nl_functions = nlsp.adaptive_identification(input_generator,ref_nlsystem.GetOutput(),branches,
                                                                           nonlinear_func=nlfunc_iden)
            iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                         nonlinear_functions=nl_functions,
                                                         filter_irs=found_filter_spec,
                                                         max_harmonics=range(1,branches+1))
            nlsp.filterkernel_evaluation_sum(filter_spec_tofind,found_filter_spec)
            nlsp.filterkernel_evaluation_plot(filter_spec_tofind,found_filter_spec)
            if Plot is True:
                plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
                plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
            print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput())
            print
        print
        print

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**16
fade_out = 0.00
fade_in = 0.00
branches = 5
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
              wgn_uniform]
iden_method = [nlsp.nonlinearconvolution_powerseries_temporalreversal,
               nlsp.nonlinearconvolution_chebyshev_temporalreversal,
               nlsp.miso_identification,
               nlsp.wiener_g_identification_corr]
nl_functions_all = [nlsp.function_factory.power_series, nlsp.function_factory.chebyshev1_polynomial,
                nlsp.function_factory.legrendre_polynomial, nlsp.function_factory.hermite_polynomial]
labels = ["NL_powerseries","NL_chebyshev","MISO","WienerG"]

uniqueness_evaluation_allexceptadaptive()
uniqueness_evaluation_adaptive()