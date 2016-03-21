import numpy as np
import matplotlib.pyplot as plt
import adaptfilt as adf
import sumpf
import nlsp
import nlsp.common.plots as plot

branches = 3
input_generator = nlsp.NovakSweepGenerator_Sine(sampling_rate=48000.0,length=2**15,start_frequency=20.0,stop_frequency=20000.0)
fil = nlsp.create_bpfilter([3000,8000,10000],input_generator.GetOutput())
ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_generator.GetOutput(),
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=fil,
                                                 max_harmonics=range(1,branches+1))
input_signal = input_generator.GetOutput()

found_filter_spec, nl_functions = nlsp.adaptive_identification(input_generator,ref_nlsystem.GetOutput(),branches,nlsp.function_factory.legrendre_polynomial)
iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                             nonlinear_functions=nl_functions,
                                             filter_irs=found_filter_spec,
                                             max_harmonics=range(1,branches+1))

plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
print "SNR between Reference and Identified output with reversed filter orders: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
