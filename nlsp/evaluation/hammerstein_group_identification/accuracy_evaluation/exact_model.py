        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is possible  ###########
        ##################################################################################

import sumpf
import nlsp
import common.plot as plot

def hgmwithfilter_sweepip_evaluation():
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    inputsignal - sweep signal
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                               start_frequency=sweep_start_freq,
                                               stop_frequency=sweep_stop_freq).GetSignal()
    filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    found_filter_spec = identification.GetPower_filter_1()
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        for i,foundspec in enumerate(found_filter_spec):
            nlsp.relabelandplot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),str(i+1)+str(" filter,input"),False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),str(i+1)+str(" filter,identified"),False)
        plot.show()
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithoverlapfilter_sweepip_evaluation():
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and overlapping
                       bandpass filters as linear functions
    inputsignal - sweep signal
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    frequencies = [800,1000,1500,2000,2500]
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                               start_frequency=sweep_start_freq,
                                               stop_frequency=sweep_stop_freq).GetSignal()
    filter_spec_tofind = nlsp.create_bpfilter(frequencies,input_sweep)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    found_filter_spec = identification.GetPower_filter_1()
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        for i,foundspec in enumerate(found_filter_spec):
            nlsp.relabelandplot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),str(i+1)+str(" filter,input"),False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),str(i+1)+str(" filter,identified"),False)
        plot.show()
    print "SNR between Reference and Identified output with overlapping filters: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def linearmodel_evaluation():
    """
    Evaluation of System Identification method by linear amplification
    nonlinear system - no nonlinearity, linear amplifier as linear system
    inputsignal - sweep signal
    plot - the virtual linear system output and the identified linear system output
    expectation - utmost similarity between the two outputs
    """
    amplification = 1.0
    input_sweep = sumpf.modules.SweepGenerator(start_frequency=sweep_start_freq, stop_frequency=sweep_stop_freq,
                                               samplingrate=sampling_rate, length=sweep_length).GetSignal()
    ref_nlsystem = sumpf.modules.AmplifySignal(factor=amplification)
    ref_nlsystem.SetInput(input_sweep)
    identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                  nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=identification.GetPower_filter_1(),
                                                  max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
    print "SNR between Reference and Identified output with overlapping filters: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
branches = 5
sweep_length = 2**15
Plot = True

hgmwithfilter_sweepip_evaluation()
hgmwithoverlapfilter_sweepip_evaluation()
linearmodel_evaluation()
