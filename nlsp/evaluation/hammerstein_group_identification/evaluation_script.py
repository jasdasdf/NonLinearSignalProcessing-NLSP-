import sumpf
import nlsp

sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
sweep_length = 2**14
silence_duration = 0.00
fade_out = 0.00
fade_in = 0.00
branches = 5
iden_method = [nlsp.nonlinearconvolution_powerseries_spectralinversion]

Plot = False
Save = False

input_generator = nlsp.NovakSweepGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, fade_out= fade_out,fade_in=fade_in)

for method in iden_method:
    print method
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



