import sumpf
import nlsp
import head_specific
import common

def sweep_aliasing_evaluation():
    degree = 2
    loudspeaker = "Visaton BF45"
    sweep = "Sweep18"
    load_sweep = sumpf.modules.SignalFile(filename=common.get_filename(loudspeaker,sweep, 1),
                                    format=sumpf.modules.SignalFile.WAV_FLOAT)
    ip_sweep_signal = sumpf.modules.SplitSignal(data=load_sweep.GetSignal(), channels=[0]).GetOutput()
    branch_simple = nlsp.HammersteinModel(input_signal=ip_sweep_signal,
                                          nonlin_func=nlsp.function_factory.power_series(degree))
    branch_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=ip_sweep_signal,
                                                                nonlin_func=nlsp.function_factory.power_series(degree),
                                                                max_harm=degree)
    branch_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal,
                                                              nonlin_func=nlsp.function_factory.power_series(degree),
                                                              max_harm=degree)
    sweep_start_freq, sweep_stop_freq, sweep_duration = head_specific.get_sweep_properties(ip_sweep_signal)
    harm_simple = nlsp.get_sweep_harmonics_spectrum(ip_sweep_signal,branch_simple.GetOutput(),sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    harm_lp = nlsp.get_sweep_harmonics_spectrum(ip_sweep_signal,branch_lp.GetOutput(),sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    harm_up = nlsp.get_sweep_harmonics_spectrum(ip_sweep_signal,branch_up.GetOutput(),sweep_start_freq,sweep_stop_freq,sweep_duration,degree)
    nlsp.relabelandplot(sumpf.modules.InverseFourierTransform(harm_simple).GetSignal(),"simple",True)
    nlsp.relabelandplot(sumpf.modules.InverseFourierTransform(harm_lp).GetSignal(),"lp",True)
    nlsp.relabelandplot(sumpf.modules.InverseFourierTransform(harm_up).GetSignal(),"up",True)

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

sweep_aliasing_evaluation()