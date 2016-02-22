import sumpf
import nlsp
import common.plot as plot

sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
sweep_length = 2**18
silence_duration = 0.02
fade_out = 0.02
fade_in = 0.02
branches = 5
iden_method = [nlsp.nonlinearconvolution_powerseries,nlsp.nonlinearconvolution_chebyshev]

Plot = False
Save = False

input_signal = nlsp.WindowedSweepGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, silence_duration= silence_duration,fade_out= fade_out,fade_in=fade_in)
for method in iden_method:
    print method
    nlsp.hgmwithfilter_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.hgmwithoverlapfilter_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.linearmodel_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.hgmwithreversedfilter_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.hgmwithamplifiedfilter_evaluation(input_signal,branches,method,Plot,Save)

    nlsp.hardclipping_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.softclipping_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.doublehgm_same_evaluation(input_signal,branches,method,Plot,Save)

    nlsp.loudspeakermodel_evaluation("Sweep18","Speech2",branches,method,Plot,Save)
    nlsp.distortionbox_evaluation("Sweep18","Speech1",branches,method,Plot,Save)

    nlsp.differentlength_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.differentbranches_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.computationtime_evaluation(input_signal,branches,method,Plot,Save)


    nlsp.robustness_excitation_evaluation(input_signal,branches,method,Plot,Save)
    nlsp.robustness_noise_evaluation(input_signal,branches,method,Plot,Save)



