import sumpf
import nlsp
import time
import itertools

def differentlength_evaluation():
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    inputsignal - sweep signal
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    length = [2**15,2**16,2**17,2**18,2**19,2**20]
    for sweep_length in length:
        input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                                   start_frequency=sweep_start_freq,
                                                   stop_frequency=sweep_stop_freq).GetSignal()
        filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,
                                            len(input_sweep),branches)
        found_filter_spec = identification.GetPower_filter_1()
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        if Plot is True:
            nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        print "SNR between Reference and Identified output : %r, input length: %r" %(nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                     iden_nlsystem.GetOutput()),len(input_sweep))

def differentbranches_evaluation():
    for branches in range(2,6):
        input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                                   start_frequency=sweep_start_freq,
                                                   stop_frequency=sweep_stop_freq).GetSignal()
        filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,
                                            len(input_sweep),branches)
        found_filter_spec = identification.GetPower_filter_1()
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        if Plot is True:
            nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        print "SNR between Reference and Identified output : %r, with number of branches: %r" %(nlsp.signal_to_noise_ratio_freq_range(ref_nlsystem.GetOutput(),
                                                                                     iden_nlsystem.GetOutput(),[sweep_start_freq,sweep_stop_freq]),branches)

def computationtime_evaluation():
    branch = range(2,6)
    length = [2**15,2**16,2**17,2**18,2**19]
    for branches,sweep_length in itertools.product(branch,length):
        simulation_time_start = time.clock()
        input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                                   start_frequency=sweep_start_freq,
                                                   stop_frequency=sweep_stop_freq).GetSignal()
        filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
        nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nl_func,
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        identification_time_start = time.clock()
        identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,
                                            len(input_sweep),branches)
        found_filter_spec = identification.GetPower_filter_1()
        identification_time_stop = time.clock()
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        iden_nlsystem.GetOutput()
        simulation_time_stop = time.clock()
        simulation_time = simulation_time_stop - simulation_time_start
        identification_time = identification_time_stop - identification_time_start
        print "Signal length: %r, branches: %r, simulation time: %r, identification time: %r" %(sweep_length,branches,
                                                                                                simulation_time,
                                                                                                identification_time)


sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
branches = 5
sweep_length = 2**16
Plot = False

differentlength_evaluation()
differentbranches_evaluation()
computationtime_evaluation()