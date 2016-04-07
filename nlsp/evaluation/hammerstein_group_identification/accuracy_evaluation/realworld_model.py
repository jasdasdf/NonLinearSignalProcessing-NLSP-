import sumpf
import nlsp
import common
import head_specific
import nlsp.common.plots as plot

def split_signals():

    loudspeaker = "Visaton BF45"
    sample = ["Sweep16","Sweep18","Sweep20","Speech1","Speech2","Speech3","Music1","Noise18","Noise20"]

    for signal in sample:
        # load loudspeaker measurings
        load_sweep = sumpf.modules.SignalFile(filename=common.get_filename(loudspeaker,signal, 1),
                                        format=sumpf.modules.SignalFile.WAV_FLOAT)
        excitation = sumpf.modules.SplitSignal(data=load_sweep.GetSignal(), channels=[0]).GetOutput()
        save = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/test_signals/%s"%signal,
                                      signal=excitation,format=sumpf.modules.SignalFile.NUMPY_NPZ)


def loudspeakermodel_evaluation(input_signal,input_sample,branches,iden_method,Plot,Save):
    loudspeaker = "Visaton BF45"
    signal = input_signal
    sample = input_sample
    # load loudspeaker measurings
    load_sweep = sumpf.modules.SignalFile(filename=common.get_filename(loudspeaker,signal, 1),
                                    format=sumpf.modules.SignalFile.WAV_FLOAT)
    excitation = sumpf.modules.SplitSignal(data=load_sweep.GetSignal(), channels=[0]).GetOutput()
    response = sumpf.modules.SplitSignal(data=load_sweep.GetSignal(), channels=[1]).GetOutput()

    # identify kernel using identification methods
    found_filter_spec, nl_functions = iden_method(excitation,response,branches)
    ls_model = nlsp.HammersteinGroupModel_up(input_signal=excitation,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    nlsp.relabelandplot(ls_model.GetOutput(),"ls")
    nlsp.relabelandplot(response,"ref")

    # load sample to evaluate the loudspeaker model
    # load_sample = sumpf.modules.SignalFile(filename=common.get_filename(loudspeaker, sample, 1),
    #                                       format=sumpf.modules.SignalFile.WAV_FLOAT)
    # sample_excitation = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[0]).GetOutput()
    # sample_response = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[1]).GetOutput()
    # if len(sample_excitation) > len(excitation):
    #     sample_excitation = sumpf.modules.CutSignal(signal=sample_excitation,start=0,stop=len(excitation)).GetOutput()
    #     sample_response = sumpf.modules.CutSignal(signal=sample_response,start=0,stop=len(excitation)).GetOutput()
    # else:
    #     sample_excitation = nlsp.append_zeros(sample_excitation,length=len(excitation))
    #     sample_response = nlsp.append_zeros(sample_response,length=len(response))
    # ls_model.SetInput(sample_excitation)

    # highpass filter the output of the model to prevent amplification of low freq signals
    # prp = sumpf.modules.ChannelDataProperties()
    # prp.SetSignal(ls_model.GetOutput())
    # highpass = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),
    #                                                   frequency=100.0,transform=True,resolution=prp.GetResolution(),
    #                                                   length=prp.GetSpectrumLength()).GetSpectrum()
    # model_up_highpass = sumpf.modules.MultiplySpectrums(spectrum1=sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),
    #                                                     spectrum2=highpass).GetOutput()
    # model_up_highpass_signal = sumpf.modules.InverseFourierTransform(model_up_highpass).GetSignal()

    # save the output to the directory
    # iden = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/miso/loudspeaker/identified",
    #                                   signal=ls_model.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    # ref = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/miso/loudspeaker/reference",
    #                                   signal=sample_response,format=sumpf.modules.SignalFile.WAV_FLOAT)
    # inp = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/miso/loudspeaker/input",
    #                                   signal=sample_excitation,format=sumpf.modules.SignalFile.WAV_FLOAT)
    # print "Loudspeaker, SNR between Reference and Identified output Sample: %r" %nlsp.snr(sample_response,
    #                                                                                          ls_model.GetOutput())
    if Plot is True:
        # plot the loudspeaker op against identified op
        # nlsp.relabelandplot(sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),"identified_sample_spectrum",False)
        # nlsp.relabelandplot(sumpf.modules.FourierTransform(sample_response).GetSpectrum(),"reference_sample_spectrum",True)

        # plot the sweep prediction outputs
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),"identified_sweep_spectrum",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(response).GetSpectrum(),"reference_sweep_spectrum",True)

    print "Loudspeaker, SNR between Reference and Identified output Sweep: %r" %nlsp.snr(response,ls_model.GetOutput())

def distortionbox_evaluation(input_sweep,input_sample,branches,iden_method,Plot,Save):
    loudspeaker = "Distortion box"
    sweep = input_sweep
    sample = input_sample
    # load loudspeaker measurings
    excitation = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Measurements/Distortion box/Recording 1/input/%s"%sweep,
                                          format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    response = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Measurements/Distortion box/Recording 1/output/%s"%sweep,
                                          format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    response = sumpf.modules.SplitSignal(response,channels=[1]).GetOutput()

    # identify kernel using nonlinear convolution method
    sweep_start_freq, sweep_stop_freq, sweep_duration = head_specific.get_sweep_properties(excitation)
    found_filter_spec, nl_functions = iden_method(excitation,response,sweep_start_freq,sweep_stop_freq,
                                        sweep_duration,branches)

    # use identified kernel in nl convolution hammerstein model
    ls_model = nlsp.HammersteinGroupModel_up(nonlinear_functions=nl_functions,
                                       filter_irs=found_filter_spec,max_harmonics=range(1,branches+1))

    # load sample to evaluate the loudspeaker model
    sample_excitation = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Measurements/Distortion box/Recording 1/input/%s"%sample,
                                          format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    sample_response = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Measurements/Distortion box/Recording 1/output/%s"%sample,
                                          format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    sample_response = sumpf.modules.SplitSignal(sample_response,channels=[1]).GetOutput()
    if len(sample_excitation) > len(excitation):
        sample_excitation = sumpf.modules.CutSignal(signal=sample_excitation,start=0,stop=len(excitation)).GetOutput()
        sample_response = sumpf.modules.CutSignal(signal=sample_response,start=0,stop=len(excitation)).GetOutput()
    else:
        sample_excitation = nlsp.append_zeros(sample_excitation,length=len(excitation))
        sample_response = nlsp.append_zeros(sample_response,length=len(response))
    ls_model.SetInput(sample_excitation)

    # highpass filter the output of the model to prevent amplification of low freq signals
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(ls_model.GetOutput())
    highpass = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),
                                                      frequency=100.0,transform=True,resolution=prp.GetResolution(),
                                                      length=prp.GetSpectrumLength()).GetSpectrum()
    model_up_highpass = sumpf.modules.MultiplySpectrums(spectrum1=sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),
                                                        spectrum2=highpass).GetOutput()
    model_up_highpass_signal = sumpf.modules.InverseFourierTransform(model_up_highpass).GetSignal()


    # save the output to the directory
    iden = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/NLconvolution/distortionbox/identified",
                                      signal=model_up_highpass_signal,format=sumpf.modules.SignalFile.WAV_FLOAT)
    ref = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/NLconvolution/distortionbox/reference",
                                      signal=sample_response,format=sumpf.modules.SignalFile.WAV_FLOAT)
    inp = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/NLconvolution/distortionbox/input",
                                      signal=sample_excitation,format=sumpf.modules.SignalFile.WAV_FLOAT)
    print "Distortion box, SNR between Reference and Identified output Sample: %r" %nlsp.snr(sample_response,
                                                                                             model_up_highpass_signal)
    if Plot is True:
        # plot the loudspeaker op against identified op
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),"identified_sample_spectrum",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(sample_response).GetSpectrum(),"reference_sample_spectrum",True)

        # plot the sweep prediction outputs
        ls_model.SetInput(excitation)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),"identified_sweep_spectrum",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(response).GetSpectrum(),"reference_sweep_spectrum",True)

    print "Distortion box, SNR between Reference and Identified output Sweep: %r" %nlsp.snr(response,ls_model.GetOutput())

def distortionbox_save():
    sampling_rate = 48000.0
    start_freq = 100.0
    stop_freq = 20000.0
    length = 2**18
    fade_out = 0.05
    fade_in = 0.10

    sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    save_sine = sumpf.modules.SignalFile(filename="F:/nl_recordings/sine_f",
                                      signal=sine.GetOutput(),format=sumpf.modules.SignalFile.NUMPY_NPZ)
    save_cos = sumpf.modules.SignalFile(filename="F:/nl_recordings/cos_f",
                                      signal=cos.GetOutput(),format=sumpf.modules.SignalFile.NUMPY_NPZ)

    fade_out = 0.0
    fade_in = 0.0
    sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    save_sine = sumpf.modules.SignalFile(filename="F:/nl_recordings/sine",
                                      signal=sine.GetOutput(),format=sumpf.modules.SignalFile.NUMPY_NPZ)
    save_cos = sumpf.modules.SignalFile(filename="F:/nl_recordings/cos",
                                      signal=cos.GetOutput(),format=sumpf.modules.SignalFile.NUMPY_NPZ)

def distortionbox_model(Plot=True):
    sampling_rate = 48000.0
    start_freq = 100.0
    stop_freq = 20000.0
    length = 2**18
    fade_out = 0.00
    fade_in = 0.00
    branches = 3

    sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)

    op_sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sine.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    op_sine = sumpf.modules.SplitSignal(data=op_sine.GetSignal(),channels=[1]).GetOutput()

    found_filter_spec, nl_functions = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine,op_sine,branches)
    # found_filter_spec, nl_functions = nlsp.adaptive_identification(sine.GetOutput(),op_sine,branches,nlsp.function_factory.power_series,iterations=5,
    #                                                                step_size=0.002,filtertaps=len(found_filter_spec[0]),algorithm=nlsp.multichannel_nlms_ideal,
    #                                                                init_coeffs=found_filter_spec)
    iden_nlsystem_sine = nlsp.HammersteinGroupModel_up(input_signal=sine.GetOutput(),
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    linear_op = nlsp.linear_identification_temporalreversal(sine,op_sine,sine.GetOutput())
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),"Reference System",show=False,line='b-')
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sine.GetOutput()).GetSpectrum(),"NL Identified System",show=False,line='r-')
        plot.relabelandplot(sumpf.modules.FourierTransform(linear_op).GetSpectrum(),"Linear Identified System",show=True,line='g-')
        # plot.relabelandplot(sumpf.modules.CutSignal(op_sine,stop=48000).GetOutput(),"Reference output",show=False)
        # plot.relabelandplot(sumpf.modules.CutSignal(iden_nlsystem_sine.GetOutput(),stop=48000).GetOutput(),"Identified output",show=False)
        # plot.relabelandplot(sumpf.modules.CutSignal(linear_op,stop=48000).GetOutput(),"linear output",show=True)
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

def adaptive_distortionbox_model(Plot=True):
    sampling_rate = 48000.0
    start_freq = 100.0
    stop_freq = 20000.0
    length = 2**18
    fade_out = 0.00
    fade_in = 0.00
    branches = 5

    sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/Speech1.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    op_sine = sumpf.modules.SplitSignal(data=sine.GetSignal(),channels=[1]).GetOutput()
    ip_sine = sumpf.modules.SplitSignal(data=sine.GetSignal(),channels=[0]).GetOutput()

    found_filter_spec, nl_functions = nlsp.adaptive_identification(ip_sine,op_sine,branches)
    iden_nlsystem_sine = nlsp.HammersteinGroupModel_up(input_signal=ip_sine,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        # plot.relabelandplot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),"Reference System",show=False,line='b-')
        # plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem_sine.GetOutput()).GetSpectrum(),"NL Identified System",show=False,line='r-')
        # plot.relabelandplot(sumpf.modules.FourierTransform(linear_op).GetSpectrum(),"Linear Identified System",show=True,line='g-')
        plot.relabelandplot(sumpf.modules.CutSignal(op_sine,stop=48000).GetOutput(),"Reference output",show=False)
        plot.relabelandplot(sumpf.modules.CutSignal(iden_nlsystem_sine.GetOutput(),stop=48000).GetOutput(),"Identified output",show=False)
    print "SNR between Reference and Identified output, nonlinear: %r" %nlsp.snr(op_sine, iden_nlsystem_sine.GetOutput())

