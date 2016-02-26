import sumpf
import nlsp

sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
sweep_length = 2**18
fade_out = 0.05
fade_in = 0.50
branches = 5
iden_method = [nlsp.nonlinearconvolution_powerseries_temporalreversal,nlsp.nonlinearconvolution_powerseries_spectralinversion,
               nlsp.nonlinearconvolution_chebyshev_temporalreversal,nlsp.nonlinearconvolution_chebyshev_spectralinversion]

Plot = False
Save = False

sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, fade_out= fade_out,fade_in=fade_in)
cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, fade_out= fade_out,fade_in=fade_in)
excitation = [sine,sine,cos,cos]

for method,input_generator in zip(iden_method,excitation):
    print method,input_generator
    # nlsp.audio_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmwithfilter_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmwithoverlapfilter_evaluation(input_generator,branches,method,Plot)
    nlsp.linearmodel_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmwithreversedfilter_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmwithamplifiedfilter_evaluation(input_generator,branches,method,Plot)

    nlsp.hardclipping_evaluation(input_generator,branches,method,Plot)
    nlsp.softclipping_evaluation(input_generator,branches,method,Plot)
    nlsp.doublehgm_same_evaluation(input_generator,branches,method,Plot)

    nlsp.differentlength_evaluation(input_generator,branches,method,Plot)
    nlsp.differentbranches_evaluation(input_generator,branches,method,Plot)
    nlsp.computationtime_evaluation(input_generator,branches,method,Plot)

    nlsp.robustness_excitation_evaluation(input_generator,branches,method,Plot)
    nlsp.robustness_noise_evaluation(input_generator,branches,method,Plot)

    # nlsp.loudspeakermodel_evaluation("Sweep18","Speech2",branches,method,Plot,Save)
    # nlsp.distortionbox_evaluation("Sweep18","Speech1",branches,method,Plot,Save)



