import sumpf
import nlsp
import nlsp.common.plots as plot

def wgnasreference():

    branches = 3
    sampling_rate = 48000.0
    length = 2**18
    start_freq = 100.0
    stop_freq = 20000.0
    fade_out = 0.00
    fade_in = 0.00
    filter_taps = 2**11

    # input generator
    sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)

    # real world reference system, load input and output noise and sweeps
    load_noise = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/Noise18.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sine.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_cosine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/cos.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    output_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[1]).GetOutput()
    input_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[0]).GetOutput()
    output_sine = sumpf.modules.SplitSignal(data=load_sine.GetSignal(),channels=[1]).GetOutput()
    output_cos = sumpf.modules.SplitSignal(data=load_cosine.GetSignal(),channels=[1]).GetOutput()
    impulse = sumpf.modules.ImpulseGenerator(length=filter_taps,samplingrate=sampling_rate).GetSignal()

    # initialize hgm
    iden_nlsystem = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=[impulse,]*branches)

    # # only sine based system identification
    # found_filter_spec_sine, nl_function_sine = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine_g,output_sine,branches)
    # iden_nlsystem.SetInput(signal=input_noise)
    # iden_nlsystem.SetNLFunctions(nl_function_sine)
    # iden_nlsystem.SetFilterIRS(found_filter_spec_sine)
    # plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power noise",show=False)
    # print "SNR between Reference and Identified output Sine: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # only cosine based system identification
    found_filter_spec_cos, nl_function_cos = nlsp.nonlinearconvolution_chebyshev_temporalreversal(cos_g,output_cos,branches)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_cos)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cos)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified cheby noise",show=False)
    print "SNR between Reference and Identified output Cos: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # only noise based system identification
    found_filter_spec_adapt, nl_function_adapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_adapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_adapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Adapt noise",show=False)
    print "SNR between Reference and Identified output Adapt: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # # sine based as init coeff for noise based system identification
    # found_filter_spec_sine_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_sine,length=filter_taps)
    # found_filter_spec_sineadapt, nl_function_sineadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
    #                                                                step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength)
    # iden_nlsystem.SetInput(signal=input_noise)
    # iden_nlsystem.SetNLFunctions(nl_function_sineadapt)
    # iden_nlsystem.SetFilterIRS(found_filter_spec_sineadapt)
    # plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power Adapt noise",show=False)
    # print "SNR between Reference and Identified output Sine Adapt: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    # cos based as init coeff for noise based system identification
    found_filter_spec_cos_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_cos,length=filter_taps)
    found_filter_spec_cosadapt, nl_function_cosadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,
                                                                                    nonlinear_func=nlsp.function_factory.chebyshev1_polynomial)
    iden_nlsystem.SetInput(signal=input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_cosadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cosadapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt noise",show=False)
    print "SNR between Reference and Identified output Cos Adapt: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())

    plot.relabelandplotphase(sumpf.modules.FourierTransform(output_noise).GetSpectrum(),"Reference Noise",show=True)

def sineasreferencerealworld():

    branches = 3
    sampling_rate = 48000.0
    length = 2**18
    start_freq = 100.0
    stop_freq = 20000.0
    fade_out = 0.00
    fade_in = 0.00
    filter_taps = 2**11

    # input generator
    sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)

    # real world reference system, load input and output noise and sweeps
    load_noise = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/Noise18.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sine.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_cosine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/cos.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
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
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power sine",show=False)
    print "SNR between Reference and Identified output Sine: %r" %nlsp.snr(output_sine, iden_nlsystem.GetOutput())

    # only cosine based system identification
    found_filter_spec_cos, nl_function_cos = nlsp.nonlinearconvolution_chebyshev_temporalreversal(cos_g,output_cos,branches)
    iden_nlsystem.SetInput(signal=sine_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_cos)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cos)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified cheby sine",show=False)
    print "SNR between Reference and Identified output Cos: %r" %nlsp.snr(output_sine, iden_nlsystem.GetOutput())

    # only noise based system identification
    found_filter_spec_adapt, nl_function_adapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False)
    iden_nlsystem.SetInput(signal=sine_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_adapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_adapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Adapt sine",show=False)
    print "SNR between Reference and Identified output Adapt: %r" %nlsp.snr(output_sine, iden_nlsystem.GetOutput())

    # sine based as init coeff for noise based system identification
    found_filter_spec_sine_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_sine,length=filter_taps)
    found_filter_spec_sineadapt, nl_function_sineadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength,nonlinear_func=nlsp.function_factory.power_series)
    iden_nlsystem.SetInput(signal=sine_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_sineadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_sineadapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified power Adapt sine",show=False)
    print "SNR between Reference and Identified output Sine Adapt: %r" %nlsp.snr(output_sine, iden_nlsystem.GetOutput())

    # cos based as init coeff for noise based system identification
    found_filter_spec_cos_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_cos,length=filter_taps)
    found_filter_spec_cosadapt, nl_function_cosadapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,nonlinear_func=nlsp.function_factory.chebyshev1_polynomial)
    iden_nlsystem.SetInput(signal=sine_g.GetOutput())
    iden_nlsystem.SetNLFunctions(nl_function_cosadapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_cosadapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt sine",show=False)
    print "SNR between Reference and Identified output Cos Adapt: %r" %nlsp.snr(output_sine, iden_nlsystem.GetOutput())

    plot.relabelandplotphase(sumpf.modules.FourierTransform(output_sine).GetSpectrum(),"Reference sine",show=True)

def loudspeaker_model_adaptive():
    """
    Realworld nonlinear system(Loudspeaker) Model using adaptive system identification
    """
    branches = 3
    filter_taps = 2**11

    # real world reference system, load input and output noise
    load_noise = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/Noise18.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    output_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[1]).GetOutput()
    input_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[0]).GetOutput()
    impulse = sumpf.modules.ImpulseGenerator(length=filter_taps,samplingrate=input_noise.GetSamplingRate()).GetSignal()

    # initialize hgm
    iden_nlsystem = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=[impulse,]*branches)

    # only noise based adaptive system identification
    found_filter_spec_adapt, nl_function_adapt = nlsp.adaptive_identification(input_generator=input_noise,outputs=output_noise,iterations=1,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False)
    iden_nlsystem.SetInput(input_noise)
    iden_nlsystem.SetNLFunctions(nl_function_adapt)
    iden_nlsystem.SetFilterIRS(found_filter_spec_adapt)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Adapt sine",show=False)
    print "SNR between Reference and Identified output Noise signal: %r" %nlsp.snr(output_noise, iden_nlsystem.GetOutput())
    plot.relabelandplotphase(sumpf.modules.FourierTransform(output_noise).GetSpectrum(),"Reference Noise",show=True)

    load_sample = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/Speech1.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)

    output_sample = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[1]).GetOutput()
    input_sample = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[0]).GetOutput()

    iden_nlsystem.SetInput(input_sample)

    # save the output to the directory
    iden = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/sim/identified",
                                      signal=iden_nlsystem.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    ref = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/sim/reference",
                                      signal=output_sample,format=sumpf.modules.SignalFile.WAV_FLOAT)
    inp = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/sim/input",
                                      signal=input_sample,format=sumpf.modules.SignalFile.WAV_FLOAT)
    print "Distortion box, SNR between Reference and Identified output Sample,nl: %r" %nlsp.snr(output_sample,
                                                                                             iden_nlsystem.GetOutput())

def loudspeaker_model_sweep(Plot=True):
    sampling_rate = 48000.0
    start_freq = 100.0
    stop_freq = 20000.0
    length = 2**18
    fade_out = 0.00
    fade_in = 0.00
    branches = 3

    sine = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)

    op_sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sine.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    op_sine = sumpf.modules.SplitSignal(data=op_sine.GetSignal(),channels=[1]).GetOutput()

    found_filter_spec, nl_functions = nlsp.nonlinearconvolution_chebyshev_adaptive(sine,op_sine,branches)
    iden_nlsystem_sine = nlsp.HammersteinGroupModel_up(input_signal=sine.GetOutput(),
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    linear_op = nlsp.linear_identification_temporalreversal(sine,op_sine,sine.GetOutput())
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),"Reference System",show=False,line='b-')
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sine.GetOutput()).GetSpectrum(),"NL Identified System",show=False,line='r-')
        plot.relabelandplot(sumpf.modules.FourierTransform(linear_op).GetSpectrum(),"Linear Identified System",show=True,line='g-')
    print "SNR between Reference and Identified output, nonlinear: %r" %nlsp.snr(op_sine, iden_nlsystem_sine.GetOutput())
    print "SNR between Reference and Identified output, linear: %r" %nlsp.snr(op_sine, linear_op)

    load_sample = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/Speech1.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sample = nlsp.append_zeros(load_sample.GetSignal())

    ref_sample = sumpf.modules.SplitSignal(data=load_sample,channels=[1]).GetOutput()
    ip_sample = sumpf.modules.SplitSignal(data=load_sample,channels=[0]).GetOutput()

    iden_nlsystem_sine.SetInput(ip_sample)
    linear_op = nlsp.linear_identification_temporalreversal(sine, op_sine, ip_sample)

    # save the output to the directory
    iden = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sim/identified",
                                      signal=iden_nlsystem_sine.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    ref = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sim/reference",
                                      signal=ref_sample,format=sumpf.modules.SignalFile.WAV_FLOAT)
    inp = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sim/input",
                                      signal=ip_sample,format=sumpf.modules.SignalFile.WAV_FLOAT)
    linear = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sim/linear",
                                      signal=linear_op,format=sumpf.modules.SignalFile.WAV_FLOAT)
    print "Distortion box, SNR between Reference and Identified output Sample,nl: %r" %nlsp.snr(ref_sample,
                                                                                             iden_nlsystem_sine.GetOutput())
    print "Distortion box, SNR between Reference and Identified output Sample,l: %r" %nlsp.snr(ref_sample,
                                                                                             linear_op)
loudspeaker_model_adaptive()
loudspeaker_model_sweep()