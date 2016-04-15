import numpy
import sumpf
import nlsp
import nlsp.common.plots as plot
import itertools

# Applicable to only virtual nonlinear system
# Find which Nonlinear function is better for adaptive system identification?
# It varies based on the choice of input signal. Test all the possibilites to find the relation between the distribution and nonlinear function.
# Orthogonal polynomials and their corresponding orthogonal probablity distribution is the best choice for adaptive identification.

def adaptive_polynomial_evaluation():
    for input_generator,nlfunc in itertools.product(excitation,nl_functions):
        print input_generator
        print nlfunc
        input_signal = input_generator.GetOutput()
        filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        found_filter_spec, nl_func = nlsp.adaptive_identification(input_generator,ref_nlsystem.GetOutput(),branches,nonlinear_func=nlfunc)
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_func,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        nlsp.filterkernel_evaluation_sum(filter_spec_tofind,found_filter_spec)
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
        print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
        print
        print

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**18
fade_out = 0.00
fade_in = 0.00
branches = 3
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
gamma = sumpf.modules.NoiseGenerator.GammaDistribution()

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
wgn_gamma = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=gamma)
excitation = [wgn_gamma, wgn_normal, wgn_uniform]
nl_functions = [nlsp.function_factory.power_series, nlsp.function_factory.chebyshev1_polynomial,
                nlsp.function_factory.legrendre_polynomial, nlsp.function_factory.hermite_polynomial]
adaptive_polynomial_evaluation()