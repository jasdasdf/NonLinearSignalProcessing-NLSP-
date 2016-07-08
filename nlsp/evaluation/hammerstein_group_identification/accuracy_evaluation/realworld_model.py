import os
import sumpf
import nlsp
import nlsp.common.plots as plot

def loudspeaker_evaluation_all(branches=3,Plot=True):

    branches = branches
    sampling_rate = 48000.0
    length = 2**18
    start_freq = 100.0
    stop_freq = 20000.0
    fade_out = 0.02
    fade_in = 0.02
    filter_taps = 2**10
    iterations = 5
    source_dir = "C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/"

    # input generator
    sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)

    # real world reference system, load input and output noise and sweeps
    load_noise = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"Noise18.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"sine_f.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_cosine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"cos_f.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sample = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"Music1.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    output_sample = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[1]).GetOutput()
    input_sample = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[0]).GetOutput()
    output_sample = nlsp.change_length_signal(output_sample,2**18)
    input_sample = nlsp.change_length_signal(input_sample,2**18)
    output_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[1]).GetOutput()
    input_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[0]).GetOutput()
    output_sine = sumpf.modules.SplitSignal(data=load_sine.GetSignal(),channels=[1]).GetOutput()
    output_cos = sumpf.modules.SplitSignal(data=load_cosine.GetSignal(),channels=[1]).GetOutput()
    impulse = sumpf.modules.ImpulseGenerator(length=filter_taps,samplingrate=sampling_rate).GetSignal()

    # linear identification
    kernel_linear,nlfunc = nlsp.linear_identification(sine_g,output_sine,branches)
    iden_nlsystem_linear = nlsp.HammersteinGroupModel_up(filter_irs=kernel_linear,nonlinear_functions=nlfunc)

    # linear identification
    kernel_linear_hgm,nlfunc_hgm = nlsp.linear_identification_powerhgm(sine_g,output_sine,branches)
    iden_nlsystem_linear_hgm = nlsp.HammersteinGroupModel_up(filter_irs=kernel_linear_hgm,nonlinear_functions=nlfunc_hgm)

    # only sine based system identification
    # found_filter_spec_sine, nl_function_sine = nlsp.systemidentification("LS",nlsp.nonlinearconvolution_powerseries_temporalreversal,
    #                                                                      branches,sine_g,output_sine)
    found_filter_spec_sine, nl_function_sine = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine_g,output_sine,branches)
    iden_nlsystem_sine = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sine,
                                                  filter_irs=found_filter_spec_sine)

    # only cosine based system identification
    # found_filter_spec_cos, nl_function_cos = nlsp.systemidentification("LS",nlsp.nonlinearconvolution_chebyshev_temporalreversal,
    #                                                                    branches,cos_g,output_cos)
    found_filter_spec_cos, nl_function_cos = nlsp.nonlinearconvolution_chebyshev_temporalreversal(cos_g,output_cos,branches)
    iden_nlsystem_cos = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cos,
                                                  filter_irs=found_filter_spec_cos)

    # only noise based system identification
    # found_filter_spec_adapt, nl_function_adapt = nlsp.adaptive_identification_legendre(input_generator=input_noise,outputs=output_noise,iterations=iterations,branches=branches,
    #                                                                step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False)
    # iden_nlsystem_adapt = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_adapt,
    #                                               filter_irs=found_filter_spec_adapt)

    # sine based as init coeff for noise based system identification
    # found_filter_spec_sine_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_sine,length=filter_taps)
    # found_filter_spec_sineadapt, nl_function_sineadapt = nlsp.adaptive_identification_legendre(input_generator=input_noise,outputs=output_noise,iterations=iterations,branches=branches,
    #                                                                step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength)
    # iden_nlsystem_sineadapt = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sineadapt,
    #                                               filter_irs=found_filter_spec_sineadapt)

    # cos based as init coeff for noise based system identification
    # found_filter_spec_cos_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_cos,length=filter_taps)
    # found_filter_spec_cosadapt, nl_function_cosadapt = nlsp.adaptive_identification_powerseries(input_generator=input_noise,outputs=output_noise,iterations=iterations,branches=branches,
    #                                                                step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,
    #                                                                                 nonlinear_func=nlsp.function_factory.chebyshev1_polynomial)
    # iden_nlsystem_cosadapt = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cosadapt,
    #                                               filter_irs=found_filter_spec_cosadapt)

    # set excitation as input
    iden_nlsystem_linear.SetInput(sine_g.GetOutput())
    iden_nlsystem_linear_hgm.SetInput(sine_g.GetOutput())
    iden_nlsystem_sine.SetInput(sine_g.GetOutput())
    iden_nlsystem_cos.SetInput(cos_g.GetOutput())
    # iden_nlsystem_adapt.SetInput(input_noise)
    # iden_nlsystem_sineadapt.SetInput(input_noise)
    # iden_nlsystem_cosadapt.SetInput(input_noise)
    plot.relabelandplot(sumpf.modules.FourierTransform(output_sine).GetSpectrum(),"Reference system",show=False)
    plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sine.GetOutput()).GetSpectrum(),"Sweep based system identification",show=False)
    plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_linear.GetOutput()).GetSpectrum(),"Linear identified system",show=True)


    if Plot is True:
        # plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sine.GetOutput()).GetSpectrum(),"Identified power",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(output_sine).GetSpectrum(),"Reference system",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_linear.GetOutput()).GetSpectrum(),"Linear identified system",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sineadapt.GetOutput()).GetSpectrum(),"sweep-adaptive output",show=True)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_cos.GetOutput()).GetSpectrum(),"Identified cheby",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(output_cos).GetSpectrum(),"Reference cheby",show=True)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_adapt.GetOutput()).GetSpectrum(),"Identified Adapt noise",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sineadapt.GetOutput()).GetSpectrum(),"Identified power Adapt noise",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_cosadapt.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt noise",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(output_noise).GetSpectrum(),"Reference Adapt noise",show=True)

    print "SNR between Reference and Identified output linear: %r" %nlsp.snr(output_sine, iden_nlsystem_linear.GetOutput())
    print "SNR between Reference and Identified output linear hgm: %r" %nlsp.snr(output_sine, iden_nlsystem_linear_hgm.GetOutput())
    print "SNR between Reference and Identified output Powerseries NL convolution: %r" %nlsp.snr(output_sine, iden_nlsystem_sine.GetOutput())
    print "SNR between Reference and Identified output Chebyshev NL convolution: %r" %nlsp.snr(output_cos, iden_nlsystem_cos.GetOutput())
    print "SNR between Reference and Identified output Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem_adapt.GetOutput())
    print "SNR between Reference and Identified output Powerseries Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem_sineadapt.GetOutput())
    # print "SNR between Reference and Identified output Chebyshev Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem_cosadapt.GetOutput())

    # set sample as input
    iden_nlsystem_linear.SetInput(input_sample)
    iden_nlsystem_linear_hgm.SetInput(input_sample)
    iden_nlsystem_sine.SetInput(input_sample)
    iden_nlsystem_cos.SetInput(input_sample)
    iden_nlsystem_adapt.SetInput(input_sample)
    iden_nlsystem_sineadapt.SetInput(input_sample)
    # iden_nlsystem_cosadapt.SetInput(input_sample)


    # if Plot is True:
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sine.GetOutput()).GetSpectrum(),"Identified power",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_cos.GetOutput()).GetSpectrum(),"Identified cheby",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_adapt.GetOutput()).GetSpectrum(),"Identified Adapt noise",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sineadapt.GetOutput()).GetSpectrum(),"Identified power Adapt noise",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_cosadapt.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt noise",show=False)
    #     plot.relabelandplot(sumpf.modules.FourierTransform(output_sample).GetSpectrum(),"Reference Adapt noise",show=True)

    print "SNR between Reference and Identified output linear: %r" %nlsp.snr(output_sample, iden_nlsystem_linear.GetOutput())
    print "SNR between Reference and Identified output linear hgm: %r" %nlsp.snr(output_sample, iden_nlsystem_linear_hgm.GetOutput())
    print "SNR between Reference and Identified output Powerseries NL convolution: %r" %nlsp.snr(output_sample, iden_nlsystem_sine.GetOutput())
    print "SNR between Reference and Identified output Chebyshev NL convolution: %r" %nlsp.snr(output_sample, iden_nlsystem_cos.GetOutput())
    print "SNR between Reference and Identified output Adaptive: %r" %nlsp.snr(output_sample, iden_nlsystem_adapt.GetOutput())
    print "SNR between Reference and Identified output Powerseries Adaptive: %r" %nlsp.snr(output_sample, iden_nlsystem_sineadapt.GetOutput())
    # print "SNR between Reference and Identified output Chebyshev Adaptive: %r" %nlsp.snr(output_sample, iden_nlsystem_cosadapt.GetOutput())


def db_evaluation_all(branches=3,Plot=False):

    branches = branches
    sampling_rate = 48000.0
    length = 2**18
    start_freq = 100.0
    stop_freq = 20000.0
    fade_out = 0.02
    fade_in = 0.02
    filter_taps = 2**10
    iterations = 5
    source_dir = "C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/"

    # input generator
    sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)

    # real world reference system, load input and output noise and sweeps
    load_noise = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"Noise18.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"sine_f.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_cosine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"cos_f.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sample = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"Speech1.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    output_sample = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[1]).GetOutput()
    input_sample = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[0]).GetOutput()
    output_sample = nlsp.change_length_signal(output_sample,2**18)
    input_sample = nlsp.change_length_signal(input_sample,2**18)
    output_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[1]).GetOutput()
    input_noise = sumpf.modules.SplitSignal(data=load_noise.GetSignal(),channels=[0]).GetOutput()
    output_sine = sumpf.modules.SplitSignal(data=load_sine.GetSignal(),channels=[1]).GetOutput()
    output_cos = sumpf.modules.SplitSignal(data=load_cosine.GetSignal(),channels=[1]).GetOutput()
    impulse = sumpf.modules.ImpulseGenerator(length=filter_taps,samplingrate=sampling_rate).GetSignal()

    # linear identification
    kernel_linear = nlsp.linear_identification_temporalreversal(sine_g,output_sine)
    iden_nlsystem_linear = nlsp.AliasCompensatingHammersteinModelUpandDown(filter_impulseresponse=kernel_linear)

    # only sine based system identification
    # found_filter_spec_sine, nl_function_sine = nlsp.systemidentification("LS",nlsp.nonlinearconvolution_powerseries_temporalreversal,
    #                                                                      branches,sine_g,output_sine)
    found_filter_spec_sine, nl_function_sine = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine_g,output_sine,branches)
    iden_nlsystem_sine = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sine,
                                                  filter_irs=found_filter_spec_sine)

    # only cosine based system identification
    # found_filter_spec_cos, nl_function_cos = nlsp.systemidentification("LS",nlsp.nonlinearconvolution_chebyshev_temporalreversal,
    #                                                                    branches,cos_g,output_cos)
    found_filter_spec_cos, nl_function_cos = nlsp.nonlinearconvolution_chebyshev_temporalreversal(cos_g,output_cos,branches)
    iden_nlsystem_cos = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cos,
                                                  filter_irs=found_filter_spec_cos)

    # only noise based system identification
    found_filter_spec_adapt, nl_function_adapt = nlsp.adaptive_identification_powerseries(input_generator=input_noise,outputs=output_noise,iterations=iterations,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False)
    iden_nlsystem_adapt = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_adapt,
                                                  filter_irs=found_filter_spec_adapt)

    # # sine based as init coeff for noise based system identification
    found_filter_spec_sine_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_sine,length=filter_taps)
    found_filter_spec_sineadapt, nl_function_sineadapt = nlsp.adaptive_identification_powerseries(input_generator=input_noise,outputs=output_noise,iterations=iterations,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength)
    iden_nlsystem_sineadapt = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sineadapt,
                                                  filter_irs=found_filter_spec_sineadapt)

    # cos based as init coeff for noise based system identification
    found_filter_spec_cos_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_cos,length=filter_taps)
    found_filter_spec_cosadapt, nl_function_cosadapt = nlsp.adaptive_identification_powerseries(input_generator=input_noise,outputs=output_noise,iterations=iterations,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,
                                                                                    nonlinear_func=nlsp.function_factory.chebyshev1_polynomial)
    iden_nlsystem_cosadapt = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cosadapt,
                                                  filter_irs=found_filter_spec_cosadapt)

    # set excitation as input
    iden_nlsystem_linear.SetInput(sine_g.GetOutput())
    iden_nlsystem_sine.SetInput(sine_g.GetOutput())
    iden_nlsystem_cos.SetInput(cos_g.GetOutput())
    iden_nlsystem_adapt.SetInput(input_noise)
    iden_nlsystem_sineadapt.SetInput(input_noise)
    iden_nlsystem_cosadapt.SetInput(input_noise)


    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sine.GetOutput()).GetSpectrum(),"Identified power",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(output_sine).GetSpectrum(),"Reference power",show=True)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_cos.GetOutput()).GetSpectrum(),"Identified cheby",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(output_cos).GetSpectrum(),"Reference cheby",show=True)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_adapt.GetOutput()).GetSpectrum(),"Identified Adapt noise",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sineadapt.GetOutput()).GetSpectrum(),"Identified power Adapt noise",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_cosadapt.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt noise",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(output_noise).GetSpectrum(),"Reference Adapt noise",show=True)

    print "SNR between Reference and Identified output linear: %r" %nlsp.snr(output_sine, iden_nlsystem_linear.GetOutput())
    print "SNR between Reference and Identified output Powerseries NL convolution: %r" %nlsp.snr(output_sine, iden_nlsystem_sine.GetOutput())
    print "SNR between Reference and Identified output Chebyshev NL convolution: %r" %nlsp.snr(output_cos, iden_nlsystem_cos.GetOutput())
    print "SNR between Reference and Identified output Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem_adapt.GetOutput())
    print "SNR between Reference and Identified output Powerseries Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem_sineadapt.GetOutput())
    print "SNR between Reference and Identified output Chebyshev Adaptive: %r" %nlsp.snr(output_noise, iden_nlsystem_cosadapt.GetOutput())

    # set sample as input
    iden_nlsystem_linear.SetInput(input_sample)
    iden_nlsystem_sine.SetInput(input_sample)
    iden_nlsystem_cos.SetInput(input_sample)
    iden_nlsystem_adapt.SetInput(input_sample)
    # iden_nlsystem_sineadapt.SetInput(input_sample)
    # iden_nlsystem_cosadapt.SetInput(input_sample)


    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sine.GetOutput()).GetSpectrum(),"Identified power",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_cos.GetOutput()).GetSpectrum(),"Identified cheby",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_adapt.GetOutput()).GetSpectrum(),"Identified Adapt noise",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sineadapt.GetOutput()).GetSpectrum(),"Identified power Adapt noise",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_cosadapt.GetOutput()).GetSpectrum(),"Identified chebyshev Adapt noise",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(output_sample).GetSpectrum(),"Reference Adapt noise",show=True)

    print "SNR between Reference and Identified output linear: %r" %nlsp.snr(output_sample, iden_nlsystem_linear.GetOutput())
    print "SNR between Reference and Identified output Powerseries NL convolution: %r" %nlsp.snr(output_sample, iden_nlsystem_sine.GetOutput())
    print "SNR between Reference and Identified output Chebyshev NL convolution: %r" %nlsp.snr(output_sample, iden_nlsystem_cos.GetOutput())
    print "SNR between Reference and Identified output Adaptive: %r" %nlsp.snr(output_sample, iden_nlsystem_adapt.GetOutput())
    print "SNR between Reference and Identified output Powerseries Adaptive: %r" %nlsp.snr(output_sample, iden_nlsystem_sineadapt.GetOutput())
    print "SNR between Reference and Identified output Chebyshev Adaptive: %r" %nlsp.snr(output_sample, iden_nlsystem_cosadapt.GetOutput())
