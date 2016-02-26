import nlsp
import nlsp.common.plots as plot

def sweep_aliasing_evaluation():
    branch_simple = nlsp.HammersteinModel(input_signal=input_sweep_signal,
                                          nonlin_func=nlsp.function_factory.power_series(degree))
    harmonics_ir1 = nlsp.get_nl_impulse_response(input_generator,branch_simple.GetOutput())
    # sep_harmonicsir1 = nlsp.get_sweep_harmonics_ir_novak(input_generator,branch_simple.GetOutput(),degree)
    # print "Sweep aliasing evaluation"
    # print "Harmonics to total harmonics ratio %r" %nlsp.harmonicsvsall_energyratio(branch_simple.GetOutput(),
    #                                                                                input_sweep_signal,degree,sweep_start_freq,
    #                                                                                sweep_stop_freq,sweep_length,degree)
    # print
    # if Plot is True:
    #     # plot.plot(harmonics_ir1,show=True)
    #     plot.plot(sep_harmonicsir1,show=True)
    harmonics = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=harmonics_ir1, harmonic_order=degree,
                                                       sweep_generator=input_generator)
    print harmonics.GetHarmonicImpulseResponse()
    # plot.plot(harmonics.GetHarmonicImpulseResponse())


degree = 5
sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 4000.0
sweep_length = 2**15
silence_duration = 0.00
fade_out = 0.00
fade_in = 0.00
Plot = True
input_generator = nlsp.NovakSweepGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq,
                                   fade_out= fade_out,fade_in=fade_in)
input_sweep_signal = input_generator.GetOutput()

sweep_aliasing_evaluation()