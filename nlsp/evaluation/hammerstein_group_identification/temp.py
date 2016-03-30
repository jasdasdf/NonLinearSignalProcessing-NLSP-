import sumpf
import nlsp
import nlsp.common.plots as plot

branches = 3
sampling_rate = 48000.0
length = (2**16)
start_freq = 20.0
stop_freq = 20000.0


input_generator = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate,length=length,start_frequency=start_freq,stop_frequency=stop_freq,
                                                fade_out=0.2,fade_in=0.1)
# t = sumpf.modules.ShiftSignal(signal=input_generator.GetOutput(),shift=length/2,circular=False).GetOutput()
# input = nlsp.append_zeros(t,length*2)
input = input_generator.GetOutput()
fil = nlsp.create_bpfilter([3000,8000,20000],input)
fil = [i for i in reversed(fil)]
ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=fil,
                                                 max_harmonics=range(1,branches+1))
output = ref_nlsystem.GetOutput()

# sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/sine_f.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
# output = sumpf.modules.SplitSignal(data=sine.GetSignal(),channels=[1]).GetOutput()
# input = sumpf.modules.SplitSignal(data=sine.GetSignal(),channels=[0]).GetOutput()

found_filter_spec, nl_functions = nlsp.adaptive_identification(input,output,branches,nlsp.function_factory.power_series,iterations=10,
                                                               step_size=0.002,filtertaps=2**10,algorithm=nlsp.multichannel_nlms_ideal)
# found_filter_spec, nl_functions = nlsp.nonlinearconvolution_powerseries_temporalreversal(input_generator,output,branches)
iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input,
                                             nonlinear_functions=nl_functions,
                                             filter_irs=found_filter_spec,
                                             max_harmonics=range(1,branches+1))

plot.relabelandplotphase(sumpf.modules.FourierTransform(output).GetSpectrum(),"Reference System",show=False)
plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
print "SNR between Reference and Identified output with reversed filter orders: %r" %nlsp.snr(output,
                                                                                             iden_nlsystem.GetOutput())


