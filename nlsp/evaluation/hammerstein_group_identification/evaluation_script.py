import sumpf
import nlsp

sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 12000.0
sweep_length = 2**16
silence_duration = 0.00
fade_out = 0.01
fade_in = 0.01
branches = 5
iden_method = [nlsp.nonlinearconvolution_powerseries_novak]

Plot = True
Save = False

input_signal1 = nlsp.WindowedSweepGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, silence_duration= silence_duration,fade_out= fade_out,fade_in=fade_in,
                                   function=sumpf.modules.SweepGenerator.Exponential)

input_signal2 = nlsp.NovakSweepGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, fade_out= fade_out,fade_in=fade_in)

# nlsp.common.plots.plot(input_signal1.GetOutput(),show=False)
# nlsp.common.plots.plot(input_signal2.GetOutput(),show=True)

# print len(input_signal2.GetOutput()),input_signal2.GetLength()


for method in iden_method:
    print method
    nlsp.hgmwithfilter_evaluation(input_signal2,branches,method,Plot,Save)
    # nlsp.hgmwithoverlapfilter_evaluation(input_signal,branches,method,Plot,Save)
    # nlsp.linearmodel_evaluation(input_signal,branches,method,Plot,Save)
    # nlsp.hgmwithreversedfilter_evaluation(input_signal,branches,method,Plot,Save)
    # nlsp.hgmwithamplifiedfilter_evaluation(input_signal,branches,method,Plot,Save)
    #
    # nlsp.hardclipping_evaluation(input_signal,branches,method,Plot,Save)
    # nlsp.softclipping_evaluation(input_signal,branches,method,Plot,Save)
    # nlsp.doublehgm_same_evaluation(input_signal,branches,method,Plot,Save)
    #
    # nlsp.loudspeakermodel_evaluation("Sweep18","Speech2",branches,method,Plot,Save)
    # nlsp.distortionbox_evaluation("Sweep18","Speech1",branches,method,Plot,Save)
    #
    # nlsp.differentlength_evaluation(input_signal,branches,method,Plot,Save)
    # nlsp.differentbranches_evaluation(input_signal,branches,method,Plot,Save)
    # nlsp.computationtime_evaluation(input_signal,branches,method,Plot,Save)


    # nlsp.robustness_excitation_evaluation(input_signal,branches,method,Plot,Save)
    # nlsp.robustness_noise_evaluation(input_signal,branches,method,Plot,Save)



