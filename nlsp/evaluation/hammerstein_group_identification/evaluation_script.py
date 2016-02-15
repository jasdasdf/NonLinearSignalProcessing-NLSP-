import nlsp
import common.plot as plot

sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 5000.0
sweep_length = 2**18
silence_duration = 0.00
fade_out = 0.00
branches = 5
iden_method = [nlsp.nonlinearconvolution_powerseries,nlsp.nonlinearconvolution_powerseries_debug,nlsp.nonlinearconvolution_chebyshev]
Plot = False

input_signal = nlsp.SweepGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, silence_duration= silence_duration,fade_out= fade_out)

for method in iden_method:
    print method
    nlsp.hgmwithfilter_evaluation(input_signal,branches,Plot,method)
    nlsp.hgmwithoverlapfilter_evaluation(input_signal,branches,Plot,method)
    nlsp.linearmodel_evaluation(input_signal,branches,Plot,method)

    nlsp.hardclipping_evaluation(input_signal,branches,Plot,method)
    nlsp.softclipping_evaluation(input_signal,branches,Plot,method)
    nlsp.doublehgm_same_evaluation(input_signal,branches,Plot,method)

    nlsp.loudspeakermodel_evaluation("Sweep18","Speech1",branches,Plot,method)
    nlsp.distortionbox_evaluation("Sweep18","Speech1",branches,Plot,method)


    nlsp.differentlength_evaluation(input_signal,branches,Plot,method)
    nlsp.differentbranches_evaluation(input_signal,branches,Plot,method)
    nlsp.computationtime_evaluation(input_signal,branches,Plot,method)


    nlsp.robustness_excitation_evaluation(input_signal,branches,Plot,method)
    nlsp.robustness_noise_evaluation(input_signal,branches,Plot,method)




