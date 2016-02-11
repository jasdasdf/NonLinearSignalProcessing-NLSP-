import sumpf
import nlsp
import itertools

def robustness_noise_evaluation():
    """
    Evaluation of System Identification method robustness by adding noise
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    inputsignal - sweep signal
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    noise_mean = [0,0.2,0.3]
    noise_sd = [0.3,0.5,1.0]
    for mean,sd in itertools.product(noise_mean,noise_sd):
        input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                                   start_frequency=sweep_start_freq,
                                                   stop_frequency=sweep_stop_freq).GetSignal()
        filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        ref_nlsystem_noise = nlsp.add_noise(ref_nlsystem.GetOutput(),sumpf.modules.NoiseGenerator.GaussianDistribution(mean,sd))
        identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,len(input_sweep),branches)
        noise_identification = nlsp.NLConvolution(input_sweep,ref_nlsystem_noise,sweep_start_freq,sweep_stop_freq,len(input_sweep),branches)
        found_filter_spec = identification.GetPower_filter_1()
        noise_filter_spec = noise_identification.GetPower_filter_1()
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        noise_iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                     filter_irs=noise_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        if Plot is True:
            nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(noise_iden_nlsystem.GetOutput()).GetSpectrum(),"Noise Identified Output",False)
            for i,foundspec in enumerate(found_filter_spec):
                nlsp.relabelandplot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),str(i+1)+str(" filter,identified"),False)
                nlsp.relabelandplot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),str(i+1)+str(" filter,input"),False)
                nlsp.relabelandplot(sumpf.modules.FourierTransform(noise_filter_spec[i]).GetSpectrum(),str(i+1)+str(" filter,identified,noise"),False)
        print "SNR between Reference and Identified output without noise: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput())
        print "SNR between Reference and Identified output with noise of sd %r and mean %r is %r" %(sd,mean,nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                                 noise_iden_nlsystem.GetOutput()))

def robustness_excitation_evaluation():
    excitation_sweep_amp = [0.5,1.0,2.0]
    sample_sweep_amp = [0.5,1.0,2.0]
    input = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                               start_frequency=sweep_start_freq,
                                               stop_frequency=sweep_stop_freq).GetSignal()
    for excitation_amp,sample_amp in itertools.product(excitation_sweep_amp,sample_sweep_amp):
        input_sweep = sumpf.modules.AmplifySignal(input=input,factor=excitation_amp).GetOutput()
        sample_sweep = sumpf.modules.AmplifySignal(input=input,factor=sample_amp).GetOutput()
        filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,len(input_sweep),branches)
        found_filter_spec = identification.GetPower_filter_1()
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=sample_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        ref_nlsystem_scaled = sumpf.modules.AmplifySignal(input=ref_nlsystem.GetOutput(),factor=sample_amp)
        if Plot is True:
            nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem_scaled.GetOutput()).GetSpectrum(),"Reference Output Scaled",False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",False)
        print "SNR between Scaled Reference(amp:%r) and Identified(amp:%r) output: %r" %(excitation_amp,sample_amp,nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput()))

sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
branches = 5
sweep_length = 2**15
Plot = True

robustness_noise_evaluation()
robustness_excitation_evaluation()
