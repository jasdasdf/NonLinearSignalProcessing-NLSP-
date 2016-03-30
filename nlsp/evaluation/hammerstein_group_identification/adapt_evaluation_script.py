import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**14
fade_out = 0.01
fade_in = 0.01
branches = 3
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
iden_method = [nlsp.adaptive_identification]

Plot = True
Save = False

sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)
square_sweep_symmetric = nlsp.SquareSweepGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq)
square_sweep_asymmetric = nlsp.SquareSweepGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq,max_value=0.8,min_value=-0.7)
soft_clip_sweep = nlsp.NLClipSignal(signal=sine.GetOutput())

excitation = [wgn_normal]

for method,input_generator in zip(iden_method,excitation):
    print method,input_generator
    # nlsp.audio_evaluation(input_generator,branches,method,Plot)
    # nlsp.puretone_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmwithfilter_evaluation(input_generator,branches,method,Plot)
    # nlsp.hgmwithoverlapfilter_evaluation(input_generator,branches,method,Plot)
    # nlsp.linearmodel_evaluation(input_generator,branches,method,Plot)
    # nlsp.hgmwithreversedfilter_evaluation(input_generator,branches,method,Plot)
    # nlsp.hgmwithamplifiedfilter_evaluation(input_generator,branches,method,Plot)
    # nlsp.hgmallpass_evaluation(input_generator,branches,method,Plot)
    # nlsp.novak_ieee_evaluation(input_generator,branches,method,Plot)
    #
    # nlsp.hardclipping_evaluation(input_generator,branches,method,Plot)
    # nlsp.softclipping_evaluation(input_generator,branches,method,Plot)
    # nlsp.doublehgm_same_evaluation(input_generator,branches,method,Plot)
    #
    # nlsp.differentlength_evaluation(input_generator,branches,method,Plot)
    # nlsp.differentbranches_evaluation(input_generator,branches,method,Plot)
    # nlsp.computationtime_evaluation(input_generator,branches,method,Plot)
    #
    # nlsp.robustness_excitation_evaluation(input_generator,branches,method,Plot)
    # nlsp.robustness_noise_evaluation(input_generator,branches,method,Plot)

    # nlsp.loudspeakermodel_evaluation("Sweep18","Speech2",branches,method,Plot,Save)
    # nlsp.distortionbox_evaluation("Sweep18","Speech1",branches,method,Plot,Save)
    # nlsp.distortionbox_save()
    # nlsp.distortionbox_model(True)
    nlsp.adaptive_distortionbox_model(True)


