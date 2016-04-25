# normal sweep vs novak's sweep comparison

import sumpf
import nlsp
import nlsp.common.plots as plot

start_frequency = 20.0
stop_frequency = 20000.0
length = 2**15
branches = 3
sampling_rate = 48000

novak_sweep = nlsp.NovakSweepGenerator_Sine(start_frequency=start_frequency, stop_frequency=stop_frequency,
                                            sampling_rate=sampling_rate, length=length)
farina_sweep = nlsp.FarinaSweepGenerator_Sine(start_frequency=start_frequency, stop_frequency=stop_frequency,
                                            sampling_rate=sampling_rate, length=length)
input_signal_novak = novak_sweep.GetOutput()
input_signal_farina = farina_sweep.GetOutput()
filter_spec_tofind_novak = nlsp.log_bpfilter(branches=branches,input=input_signal_novak)
filter_spec_tofind_farina = nlsp.log_bpfilter(branches=branches,input=input_signal_farina)

ref_nlsystem_novak = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                             filter_irs=filter_spec_tofind_novak,
                                             max_harmonics=range(1,branches+1))
ref_nlsystem_farina = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                             filter_irs=filter_spec_tofind_farina,
                                             max_harmonics=range(1,branches+1))
ref_nlsystem_novak.SetInput(input_signal_novak)
ref_nlsystem_farina.SetInput(input_signal_farina)
ir_novak = nlsp.getnl_ir(novak_sweep,ref_nlsystem_novak.GetOutput(),branches)
ir_farina = nlsp.getnl_ir(farina_sweep,ref_nlsystem_farina.GetOutput(),branches)
plot.relabelandplot(ir_novak,"NL IR with rounding",show=False)
plot.relabelandplot(ir_farina,"NL IR without rounding",show=True)