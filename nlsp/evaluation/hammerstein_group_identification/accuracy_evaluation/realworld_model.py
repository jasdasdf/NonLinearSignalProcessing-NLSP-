import os
import sumpf
import nlsp
import nlsp.common.plots as plot

def loudspeaker_evaluation_all(branches=3,Plot=False):

    branches = branches
    sampling_rate = 48000.0
    length = 2**18
    start_freq = 100.0
    stop_freq = 20000.0
    fade_out = 0.00
    fade_in = 0.00
    filter_taps = 2**11
    source_dir = "C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/"

    # input generator
    sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)

    # real world reference system, load input and output noise and sweeps
    load_noise = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"Noise18.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"sine.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_cosine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"cos.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    output_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[1]).GetOutput()
    input_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[0]).GetOutput()
    output_sine = sumpf.modules.SplitSignal(data=load_sine.GetSignal(),channels=[1]).GetOutput()
    output_cos = sumpf.modules.SplitSignal(data=load_cosine.GetSignal(),channels=[1]).GetOutput()
    impulse = sumpf.modules.ImpulseGenerator(length=filter_taps,samplingrate=sampling_rate).GetSignal()

    # initialize hgm
    iden_nlsystem = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=[impulse,]*branches)

    # only sine based system identification
    found_filter_spec_sine, nl_function_sine = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine_g,output_sine,branches)
    iden_nlsystem.SetInput(signal=sine_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_sine)
    iden_nlsystem.SetFilterIRS(found_filter_spec_sine)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power noise",show=False)
    print "SNR between Reference and Identified output Powerseries NL convolution: %r" %nlsp.snr(output_sine, iden_nlsystem.GetOutput())

    # only cosine based system identification
    found_filter_spec_cos, nl_function_cos = nlsp.nonlinearconvolution_chebyshev_temporalreversal(cos_g,output_cos,branches)
    iden_nlsystem.SetInput(signal=cos_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_cos)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cos)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified cheby noise",show=False)
    print "SNR between Reference and Identified output Chebyshev NL convolution: %r" %nlsp.snr(output_cos, iden_nlsystem.GetOutput())

    # only noise based system identification
    found_filter_spec_adapt, nl_function_adapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_adapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_adapt)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Adapt noise",show=False)
    print "SNR between Reference and Identified output Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # sine based as init coeff for noise based system identification
    found_filter_spec_sine_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_sine,length=filter_taps)
    found_filter_spec_sineadapt, nl_function_sineadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_sineadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_sineadapt)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power Adapt noise",show=False)
    print "SNR between Reference and Identified output Powerseries Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # cos based as init coeff for noise based system identification
    found_filter_spec_cos_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_cos,length=filter_taps)
    found_filter_spec_cosadapt, nl_function_cosadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,
                                                                                    nonlinear_func=nlsp.function_factory.chebyshev1_polynomial)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_cosadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cosadapt)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt noise",show=False)
    print "SNR between Reference and Identified output Chebyshev Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(output_noise).GetSpectrum(),"Reference Noise",show=True)

def distortionbox_evaluation_all(branches=3,Plot=False):

    branches = branches
    sampling_rate = 48000.0
    length = 2**18
    start_freq = 100.0
    stop_freq = 20000.0
    fade_out = 0.00
    fade_in = 0.00
    filter_taps = 2**11
    source_dir = "C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/"

    # input generator
    sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)

    # real world reference system, load input and output noise and sweeps
    load_noise = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"Noise18.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"sine.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_cosine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"cos.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    output_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[1]).GetOutput()
    input_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[0]).GetOutput()
    output_sine = sumpf.modules.SplitSignal(data=load_sine.GetSignal(),channels=[1]).GetOutput()
    output_cos = sumpf.modules.SplitSignal(data=load_cosine.GetSignal(),channels=[1]).GetOutput()
    impulse = sumpf.modules.ImpulseGenerator(length=filter_taps,samplingrate=sampling_rate).GetSignal()

    # initialize hgm
    iden_nlsystem = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=[impulse,]*branches)

    # only sine based system identification
    found_filter_spec_sine, nl_function_sine = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine_g,output_sine,branches)
    iden_nlsystem.SetInput(signal=sine_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_sine)
    iden_nlsystem.SetFilterIRS(found_filter_spec_sine)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power noise",show=False)
    print "SNR between Reference and Identified output Powerseries NL convolution: %r" %nlsp.snr(output_sine, iden_nlsystem.GetOutput())

    # only cosine based system identification
    found_filter_spec_cos, nl_function_cos = nlsp.nonlinearconvolution_chebyshev_temporalreversal(cos_g,output_cos,branches)
    iden_nlsystem.SetInput(signal=cos_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_cos)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cos)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified cheby noise",show=False)
    print "SNR between Reference and Identified output Chebyshev NL convolution: %r" %nlsp.snr(output_cos, iden_nlsystem.GetOutput())

    # only noise based system identification
    found_filter_spec_adapt, nl_function_adapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_adapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_adapt)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Adapt noise",show=False)
    print "SNR between Reference and Identified output Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # sine based as init coeff for noise based system identification
    found_filter_spec_sine_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_sine,length=filter_taps)
    found_filter_spec_sineadapt, nl_function_sineadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_sineadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_sineadapt)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power Adapt noise",show=False)
    print "SNR between Reference and Identified output Powerseries Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # cos based as init coeff for noise based system identification
    found_filter_spec_cos_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_cos,length=filter_taps)
    found_filter_spec_cosadapt, nl_function_cosadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,
                                                                                    nonlinear_func=nlsp.function_factory.chebyshev1_polynomial)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_cosadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cosadapt)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt noise",show=False)
    print "SNR between Reference and Identified output Chebyshev Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(output_noise).GetSpectrum(),"Reference Noise",show=True)