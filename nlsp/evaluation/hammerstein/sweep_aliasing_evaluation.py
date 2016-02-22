import sumpf
import nlsp
import nlsp.common.plots as plot

def sweep_aliasing_evaluation():
    branch_simple = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input_signal.GetOutput(),
                                          nonlin_func=nlsp.function_factory.power_series(degree))
    harmonics_ir = nlsp.get_sweep_harmonics_ir(input_sweep_signal,branch_simple.GetOutput(),
                                               sweep_start_freq,sweep_stop_freq,sweep_length,degree)
    # harmonics_ir = nlsp.get_impulse_response(input_sweep_signal,branch_simple.GetOutput(),sweep_stop_freq,sweep_stop_freq)
    print "Sweep aliasing evaluation"
    print "Harmonics to total harmonics ratio %r" %nlsp.harmonicsvsall_energyratio(branch_simple.GetOutput(),
                                                                                   input_sweep_signal,degree,sweep_start_freq,
                                                                                   sweep_stop_freq,sweep_length,degree)
    print
    if Plot is True:
        plot.plot(harmonics_ir)

degree = 3
sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 4000.0
sweep_length = 2**18
silence_duration = 0.02
fade_out = 0.02
fade_in = 0.02
Plot = True
input_signal = nlsp.WindowedSweepGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, silence_duration= silence_duration,fade_out= fade_out,fade_in=fade_in)
sweep_start_freq,sweep_stop_freq,sweep_length = input_signal.GetProperties()
print sweep_start_freq,sweep_stop_freq,sweep_length
input_sweep_signal = input_signal.GetOutput()

sweep_aliasing_evaluation()