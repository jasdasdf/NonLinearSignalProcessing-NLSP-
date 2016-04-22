import sumpf
import nlsp
import itertools
import nlsp.common.plots as plot

def robustness_noise_evaluation(input_generator,branches,iden_method,Plot):
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

        if Plot is True:
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",False)
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(noise_iden_nlsystem.GetOutput()).GetSpectrum(),"Noise Identified Output",True)
        print "SNR between Reference and Identified output without noise: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput())
        print "SNR between Reference and Identified output with noise of sd %r and mean %r is %r" %(sd,mean,nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 noise_iden_nlsystem.GetOutput()))

def robustness_excitation_evaluation(input_generator,branches,iden_method,Plot):

    excitation_signal_amp = [0.5,0.7,1.0,1.5,2.0]
    sample_signal_amp = [0.5,0.7,1.0,1.5,2.0]
    input = input_generator.GetOutput()
    for excitation_amp,sample_amp in itertools.product(excitation_signal_amp,sample_signal_amp):
        input_signal = sumpf.modules.AmplifySignal(input=input,factor=excitation_amp).GetOutput()
        sample_signal = sumpf.modules.AmplifySignal(input=input,factor=sample_amp).GetOutput()
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
