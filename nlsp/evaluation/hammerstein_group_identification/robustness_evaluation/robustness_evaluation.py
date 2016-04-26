import sumpf
import nlsp
import itertools
import nlsp.common.plots as plot

def robustness_noise_evaluation(input_generator,branches,iden_method,Plot,reference=None):
    """
    Evaluation of System Identification method robustness by adding noise
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    noise_mean = [0,0.3,0.5,0.7]
    noise_sd = [0.3,0.5,0.7,1.0]
    for mean,sd in itertools.product(noise_mean,noise_sd):
        input_signal = input_generator.GetOutput()
        filter_spec_tofind = nlsp.log_weightingfilter(branches=branches,input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        ref_nlsystem_noise = nlsp.add_noise(ref_nlsystem.GetOutput(),sumpf.modules.NoiseGenerator.GaussianDistribution(mean,sd))
        found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
        noise_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem_noise,branches)

        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        noise_iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=noise_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        if reference is not None:
            reference = nlsp.change_length_signal(reference,length=len(input_signal))
            ref_nlsystem.SetInput(reference)
            iden_nlsystem.SetInput(reference)
            noise_iden_nlsystem.SetInput(reference)
        if Plot is True:
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",False)
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(noise_iden_nlsystem.GetOutput()).GetSpectrum(),"Noise Identified Output",True)
        print "SNR between Reference and Identified output without noise: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput())
        print "SNR between Reference and Identified output with noise of sd %r and mean %r is %r" %(sd,mean,nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 noise_iden_nlsystem.GetOutput()))

def robustness_excitation_evaluation(input_generator,branches,iden_method,Plot,reference=None):

    excitation_signal_amp = [0.5,0.7,1.0,1.5,2.0]
    sample_signal_amp = [0.5,0.7,1.0,1.5,2.0]
    input = input_generator.GetOutput()
    for excitation_amp,sample_amp in itertools.product(excitation_signal_amp,sample_signal_amp):
        input_signal = sumpf.modules.AmplifySignal(input=input,factor=excitation_amp).GetOutput()
        sample_signal = nlsp.WhiteGaussianGenerator(sampling_rate=input_signal.GetSamplingRate(),length=len(input_signal),
                                                    distribution=sumpf.modules.NoiseGenerator.UniformDistribution(minimum=-sample_amp,maximum=sample_amp))
        sample_signal = sample_signal.GetOutput()
        filter_spec_tofind = nlsp.log_weightingfilter(branches=branches,input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=sample_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        ref_nlsystem.SetInput(sample_signal)
        if Plot is True:
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output Scaled",False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        print "SNR between Scaled Identified with(amp:%r) and Tested with(amp:%r) output: %r" %(excitation_amp,sample_amp,nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput()))

def robustness_differentexcitation_evaluation(input_generator,branches,iden_method,Plot):
    input_signal = input_generator.GetOutput()
    sampling_rate = input_signal.GetSamplingRate()
    start_freq = input_generator.GetStartFrequency()
    stop_freq = input_generator.GetStopFrequency()
    length = len(input_signal)
    normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
    uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
    pink = sumpf.modules.NoiseGenerator.PinkNoise()
    laplace = sumpf.modules.NoiseGenerator.LaplaceDistribution(mean=0.0,scale=0.3)

    sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq)
    cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq)
    wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=normal)
    wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=uniform)
    wgn_pink = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=pink)
    wgn_laplace = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=laplace)
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                  nonlinear_functions=nl_functions,
                                                  filter_irs=found_filter_spec,
                                                  max_harmonics=range(1,branches+1))
    inputs = [sine,cos,wgn_normal,wgn_uniform,wgn_pink,wgn_laplace]
    print "SNR between reference and identified output: %r" %(nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem.GetOutput()))
    for input in inputs:
        ref_nlsystem.SetInput(input.GetOutput())
        iden_nlsystem.SetInput(input.GetOutput())
        if Plot is True:
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output Scaled",False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        print "SNR between reference and identified output: %r for inputsignal: %r" %(nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                               iden_nlsystem.GetOutput()),str(input))
        print
        print
