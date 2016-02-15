import sumpf
import nlsp
import head_specific
import common.plot as plot

def sweep_aliasing_evaluation():
    degree = 5
    sweep_start_freq,sweep_stop_freq,sweep_duration = input_signal.GetProperties()
    branch_simple = nlsp.HammersteinModel(input_signal=input_signal.GetOutput(),
                                          nonlin_func=nlsp.function_factory.power_series(degree))
    branch_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input_signal.GetOutput(),
                                                                nonlin_func=nlsp.function_factory.power_series(degree),
                                                                max_harm=degree)
    branch_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=input_signal.GetOutput(),
                                                              nonlin_func=nlsp.function_factory.power_series(degree),
                                                              max_harm=degree)
    plot.plot(nlsp.get_impulse_response(input_signal.GetOutput(),branch_simple.GetNLOutput(),sweep_start_freq,sweep_stop_freq))
    # harm_simple = nlsp.get_sweep_harmonics_spectrum(input_signal.GetOutput(),branch_simple.GetOutput(),sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    # harm_lp = nlsp.get_sweep_harmonics_spectrum(input_signal.GetOutput(),branch_lp.GetOutput(),sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    # harm_up = nlsp.get_sweep_harmonics_spectrum(input_signal.GetOutput(),branch_up.GetOutput(),sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    # nlsp.relabelandplot(sumpf.modules.InverseFourierTransform(harm_simple).GetSignal(),"simple",True)
    # nlsp.relabelandplot(sumpf.modules.InverseFourierTransform(harm_lp).GetSignal(),"lp",True)
    # nlsp.relabelandplot(sumpf.modules.InverseFourierTransform(harm_up).GetSignal(),"up",True)

    # print nlsp.calculateenergy_freq(harm_simple)
    # print nlsp.calculateenergy_freq(harm_lp)
    # print nlsp.calculateenergy_freq(harm_up)
    # print
    # print
    # print nlsp.harmonicsvsall_energyratio(branch_simple.GetOutput(),ip_sweep_signal,degree,sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    # print nlsp.harmonicsvsall_energyratio(branch_lp.GetOutput(),ip_sweep_signal,degree,sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    # print nlsp.harmonicsvsall_energyratio(branch_up.GetOutput(),ip_sweep_signal,degree,sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    # print
    # print

degree = 5
sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 4000.0
sweep_length = 2**16
silence_duration = 0.02
fade_out = 0.03
branches = 5
Plot = True
input_signal = nlsp.SweepGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, silence_duration= silence_duration,fade_out= fade_out)
sweep_aliasing_evaluation()