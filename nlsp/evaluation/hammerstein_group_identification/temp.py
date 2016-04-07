import sumpf
import nlsp
import nlsp.common.plots as plot

branches = 5
sampling_rate = 48000.0
length = 2**18
start_freq = 100.0
stop_freq = 20000.0
fade_out = 0.00
fade_in = 0.00

normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
iden_method = [nlsp.nonlinearconvolution_chebyshev_temporalreversal_adaptivefilter]

sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)

excitation = [wgn_uniform,wgn_uniform,wgn_uniform]
nl_func = [nlsp.function_factory.power_series, nlsp.function_factory.chebyshev1_polynomial, nlsp.function_factory.hermite_polynomial, nlsp.function_factory.legrendre_polynomial]
Plot = ["uniform-power","uniform-cheby","uniform-hermite","uniform-legrendre"]

for input_generator, nl_f, label in zip(excitation,nl_func,Plot):

    input = input_generator.GetOutput()
    # fil = nlsp.create_bpfilter([300,1000,3000,8000,20000],input)
    # fil = [i for i in reversed(fil)]
    # ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input,
    #                                                  nonlinear_functions=nlsp.nl_branches(nl_f,branches),
    #                                                  filter_irs=fil,
    #                                                  max_harmonics=range(1,branches+1))
    # output = ref_nlsystem.GetOutput()
    noise = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/Noise20s", format=sumpf.modules.SignalFile.WAV_FLOAT)
    sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sine.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    sine = sine.GetSignal()
    noise = sumpf.modules.CutSignal(signal=noise.GetSignal(), start=0, stop=2**18).GetOutput()
    output_noise = sumpf.modules.SplitSignal(data=noise,channels=[1]).GetOutput()
    input_noise = sumpf.modules.SplitSignal(data=noise,channels=[0]).GetOutput()
    output_sine = sumpf.modules.SplitSignal(data=sine,channels=[1]).GetOutput()
    input_sine = input

    found_filter_spec_noise, nl_functions_noise = nlsp.adaptive_identification(input_noise,output_noise,branches,nl_f,iterations=5,
                                                                   step_size=0.02,filtertaps=2**10,algorithm=nlsp.multichannel_nlms_ideal,Plot=False)
    found_filter_spec_sine, nl_functions_sine = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine_g,output_sine,branches)
    iden_nlsystem_noise = nlsp.HammersteinGroupModel_up(input_signal=input_noise,
                                                 nonlinear_functions=nl_functions_noise,
                                                 filter_irs=found_filter_spec_noise,
                                                 max_harmonics=range(1,branches+1))
    iden_nlsystem_sine = nlsp.HammersteinGroupModel_up(input_signal=input,
                                                 nonlinear_functions=nl_functions_sine,
                                                 filter_irs=found_filter_spec_sine,
                                                 max_harmonics=range(1,branches+1))
    iden_nlsystem_noise.SetInput(input_sine)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(output_sine).GetSpectrum(),"Reference System",show=False)
    plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem_noise.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with reversed filter orders: %r" %nlsp.snr(output_sine,
                                                                                                 iden_nlsystem_noise.GetOutput())


