import sumpf
import nlsp
import nlsp.common.plots as plot

def adaptive_initializedwith_sweep():
    # virtial reference system
    filter_spec_tofind_noise = nlsp.log_bpfilter(branches=branches,input=wgn_uniform_g.GetOutput())
    filter_spec_tofind_sweep = nlsp.log_bpfilter(branches=branches,input=sine_g.GetOutput())
    ref_nlsystem = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind_noise,
                                                 max_harmonics=range(1,branches+1))
    ref_nlsystem.SetInput(wgn_uniform_g.GetOutput())
    output_noise = ref_nlsystem.GetOutput()
    input_noise = wgn_uniform_g.GetOutput()
    ref_nlsystem.SetFilterIRS(filter_spec_tofind_sweep)
    ref_nlsystem.SetInput(sine_g.GetOutput())
    output_sine = ref_nlsystem.GetOutput()
    ref_nlsystem.SetInput(cos_g.GetOutput())
    output_cos = ref_nlsystem.GetOutput()
    impulse = sumpf.modules.ImpulseGenerator(length=filter_taps,samplingrate=sampling_rate).GetSignal()

    # initialize hgm
    iden_nlsystem = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=[impulse,]*branches)

    # only sine based system identification
    found_filter_spec_sine, nl_function_sine = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine_g,output_sine,branches)
    iden_nlsystem.SetInput(signal=sine_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_sine)
    iden_nlsystem.SetFilterIRS(found_filter_spec_sine)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power sine",show=False)
    print "SNR between Reference and Identified output Sine: %r" %nlsp.snr(output_sine, iden_nlsystem.GetOutput())

    # only cosine based system identification
    found_filter_spec_cos, nl_function_cos = nlsp.nonlinearconvolution_chebyshev_temporalreversal(cos_g,output_cos,branches)
    iden_nlsystem.SetInput(signal=cos_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_cos)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cos)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified cheby sine",show=False)
    print "SNR between Reference and Identified output Cos: %r" %nlsp.snr(output_cos, iden_nlsystem.GetOutput())

    # only noise based system identification
    found_filter_spec_adapt, nl_function_adapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_adapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_adapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Adapt sine",show=False)
    print "SNR between Reference and Identified output Adapt: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # sine based as init coeff for noise based system identification
    found_filter_spec_sine_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_sine,length=filter_taps)
    found_filter_spec_sineadapt, nl_function_sineadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength,nonlinear_func=nlsp.function_factory.power_series)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_sineadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_sineadapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power Adapt sine",show=False)
    print "SNR between Reference and Identified output Sine Adapt: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # cos based as init coeff for noise based system identification
    found_filter_spec_cos_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_cos,length=filter_taps)
    found_filter_spec_cosadapt, nl_function_cosadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,nonlinear_func=nlsp.function_factory.chebyshev1_polynomial)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_cosadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cosadapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt sine",show=False)
    print "SNR between Reference and Identified output Cos Adapt: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    plot.relabelandplotphase(sumpf.modules.FourierTransform(output_sine).GetSpectrum(),"Reference sine",show=True)

sampling_rate = 48000.0
start_freq = 100.0
stop_freq = 20000.0
length = 2**18
fade_out = 0.00
fade_in = 0.00
filter_taps = 2**11
branches = 3
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()

Plot = True
Save = False

sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
wgn_normal_g = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
wgn_uniform_g = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)

adaptive_initializedwith_sweep()