import numpy
import os
import sumpf
import nlsp
import nlsp.common.plots as plot
import itertools

# Applicable to only virtual nonlinear system
# Find which Nonlinear function is better for adaptive system identification?
# It varies based on the choice of input signal. Test all the possibilites to find the relation between the distribution and nonlinear function.
# Orthogonal polynomials and their corresponding orthogonal probablity distribution is the best choice for adaptive identification.

def adaptive_polynomial_evaluation_virtual():
    for input_generator,nlfunc in itertools.product(excitation,nl_functions):
        print input_generator
        print nlfunc
        input_signal = input_generator.GetOutput()
        filter_spec_tofind = nlsp.log_weightingfilter(branches=branches,input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        found_filter_spec, nl_func = nlsp.adaptive_identification(input_generator,ref_nlsystem.GetOutput(),branches,nonlinear_func=nlfunc)
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_func,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        ref_nlsystem.SetInput(wgn_pink.GetOutput())
        iden_nlsystem.SetInput(wgn_pink.GetOutput())
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
        print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
        print
        print

def adaptive_polynomial_evaluation_realworld():
    # real world reference system, load input and output noise
    load_wgn_normal = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"wgn_normal_16.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_wgn_uniform = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"wgn_uniform_16.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_wgn_gamma = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"wgn_gamma_16.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_wgn_pink = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"wgn_pink_16.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    input_wgn_normal = sumpf.modules.SplitSignal(data=load_wgn_normal.GetSignal(),channels=[0]).GetOutput()
    output_wgn_normal = sumpf.modules.SplitSignal(data=load_wgn_normal.GetSignal(),channels=[1]).GetOutput()
    input_wgn_uniform = sumpf.modules.SplitSignal(data=load_wgn_uniform.GetSignal(),channels=[0]).GetOutput()
    output_wgn_uniform = sumpf.modules.SplitSignal(data=load_wgn_uniform.GetSignal(),channels=[1]).GetOutput()
    input_wgn_gamma = sumpf.modules.SplitSignal(data=load_wgn_gamma.GetSignal(),channels=[0]).GetOutput()
    output_wgn_gamma = sumpf.modules.SplitSignal(data=load_wgn_gamma.GetSignal(),channels=[1]).GetOutput()
    input_wgn_pink = sumpf.modules.SplitSignal(data=load_wgn_pink.GetSignal(),channels=[0]).GetOutput()
    output_wgn_pink = sumpf.modules.SplitSignal(data=load_wgn_pink.GetSignal(),channels=[1]).GetOutput()

    for nlfunc in nl_functions:
        print nlfunc
        found_filter_spec_normal, nl_func_normal = nlsp.adaptive_identification(input_wgn_normal,output_wgn_normal,branches,nonlinear_func=nlfunc)
        found_filter_spec_uniform, nl_func_uniform = nlsp.adaptive_identification(input_wgn_uniform,output_wgn_uniform,branches,nonlinear_func=nlfunc)
        found_filter_spec_gamma, nl_func_gamma = nlsp.adaptive_identification(input_wgn_gamma,output_wgn_gamma,branches,nonlinear_func=nlfunc)
        iden_nlsystem_normal = nlsp.HammersteinGroupModel_up(input_signal=input_wgn_normal,
                                                             nonlinear_functions=nl_func_normal,
                                                             filter_irs=found_filter_spec_normal,
                                                             max_harmonics=range(1,branches+1))
        iden_nlsystem_uniform = nlsp.HammersteinGroupModel_up(input_signal=input_wgn_uniform,
                                                             nonlinear_functions=nl_func_uniform,
                                                             filter_irs=found_filter_spec_uniform,
                                                             max_harmonics=range(1,branches+1))
        iden_nlsystem_gamma = nlsp.HammersteinGroupModel_up(input_signal=input_wgn_gamma,
                                                             nonlinear_functions=nl_func_gamma,
                                                             filter_irs=found_filter_spec_gamma,
                                                             max_harmonics=range(1,branches+1))
        iden_nlsystem_normal.SetInput(input_wgn_pink)
        iden_nlsystem_gamma.SetInput(input_wgn_pink)
        iden_nlsystem_uniform.SetInput(input_wgn_pink)
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(output_wgn_pink).GetSpectrum(),"Reference Output",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_normal.GetOutput()).GetSpectrum(),"Identified Output",show=True)
        print "SNR between Reference and Identified output without overlapping filters Normal: %r" %nlsp.snr(output_wgn_pink,
                                                                                             iden_nlsystem_normal.GetOutput())
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(output_wgn_pink).GetSpectrum(),"Reference Output",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_uniform.GetOutput()).GetSpectrum(),"Identified Output",show=True)
        print "SNR between Reference and Identified output without overlapping filters Uniform: %r" %nlsp.snr(output_wgn_pink,
                                                                                             iden_nlsystem_uniform.GetOutput())
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(output_wgn_pink).GetSpectrum(),"Reference Output",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_gamma.GetOutput()).GetSpectrum(),"Identified Output",show=True)
        print "SNR between Reference and Identified output without overlapping filters Gamma: %r" %nlsp.snr(output_wgn_pink,
                                                                                             iden_nlsystem_gamma.GetOutput())


sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**16
fade_out = 0.00
fade_in = 0.00
branches = 5
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
gamma = sumpf.modules.NoiseGenerator.GammaDistribution()
pink = sumpf.modules.NoiseGenerator.PinkNoise()
source_dir = "C:/Users/diplomand.8/Desktop/nl_recordings/rec_5_ls/"

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
wgn_pink = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=pink)
excitation = [wgn_uniform,wgn_normal,wgn_gamma]
nl_functions = [nlsp.function_factory.hermite_polynomial,nlsp.function_factory.legrendre_polynomial,
                nlsp.function_factory.power_series,nlsp.function_factory.chebyshev1_polynomial]
adaptive_polynomial_evaluation_virtual()
# adaptive_polynomial_evaluation_realworld()