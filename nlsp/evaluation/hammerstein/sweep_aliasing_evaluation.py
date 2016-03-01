import sumpf
import nlsp
import nlsp.common.plots as plot

def sweep_aliasing_evaluation():
    input_signal = input_generator.GetOutput()
    lin = sumpf.modules.ImpulseGenerator(samplingrate=input_signal.GetSamplingRate(),length=100).GetSignal()
    nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                             filter_irs= [lin,]*degree,
                                             nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,degree),
                                             max_harmonics=range(1,degree+1))
    harmonics_ir = nlsp.get_nl_impulse_response(input_generator,nlsystem.GetOutput())
    harmonics = nlsp.get_nl_harmonics(input_generator,nlsystem.GetOutput(),degree)
    print "Harmonics to total harmonics ratio %r" %nlsp.harmonicsvsall_energyratio_nl(input_generator,nlsystem.GetOutput(),
                                                                                      degree)
    plot.plot(harmonics_ir)
    plot.plot(harmonics)


degree = 5
sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 3000.0
sweep_length = 2**15
silence_duration = 0.00
fade_out = 0.00
fade_in = 0.00
Plot = True
input_generator = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq,
                                   fade_out= fade_out,fade_in=fade_in)
input_sweep_signal = input_generator.GetOutput()

sweep_aliasing_evaluation()