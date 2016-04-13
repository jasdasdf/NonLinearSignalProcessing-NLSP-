import sumpf
import nlsp
import nlsp.common.plots as plot

branches = 3
sampling_rate = 48000.0
length = 2**16
start_freq = 100.0
stop_freq = 20000.0
fade_out = 0.00
fade_in = 0.00
filter_taps = 2**11

def sweeptest():
    # input generator
    sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                           stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=filter_taps).GetSignal()
    sweep = nlsp.append_zeros(sweep,length=filter_taps*2)
    sweep = sumpf.modules.ShiftSignal(signal=sweep, shift=(filter_taps*2)/4, circular=False).GetOutput()
    sweep = sumpf.modules.ConcatenateSignals(signal1=sweep,signal2=sweep).GetOutput()
    sweep = sumpf.modules.ConcatenateSignals(signal1=sweep,signal2=sweep).GetOutput()
    sweep = sumpf.modules.ConcatenateSignals(signal1=sweep,signal2=sweep).GetOutput()
    input_signal = sweep
    filter_spec_tofind = nlsp.create_bpfilter([500,8000,20000],input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = nlsp.adaptive_identification(input_signal,ref_nlsystem.GetOutput(),branches,Plot=True,filtertaps=filter_taps,
                                                                   iterations=1)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    plot.relabelandplot(ref_nlsystem.GetOutput(),"Reference Output",show=False)
    plot.relabelandplot(iden_nlsystem.GetOutput(),"Identified Output",show=True)
    plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
    plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
    print "SNR between Reference and Identified output: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def noisetest():
    normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
    wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
    input_signal = wgn_normal.GetOutput()
    filter_spec_tofind = nlsp.create_bpfilter([500,8000,20000],input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec, nl_functions = nlsp.adaptive_identification(input_signal,ref_nlsystem.GetOutput(),branches,Plot=True)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    plot.relabelandplot(ref_nlsystem.GetOutput(),"Reference Output",show=False)
    plot.relabelandplot(iden_nlsystem.GetOutput(),"Identified Output",show=True)
    plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
    plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
    print "SNR between Reference and Identified output: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def audio_evaluation(input_generator,branches,iden_method,Plot):

    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.create_bpfilter([1000,2000,4000,8000,16000],input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    excitation = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Speech3.npz",
                                              format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    ref_nlsystem.SetInput(excitation)
    iden_nlsystem.SetInput(excitation)
    ref = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Ref",
                                      signal=ref_nlsystem.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    iden = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Iden",
                                      signal=iden_nlsystem.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

noisetest()