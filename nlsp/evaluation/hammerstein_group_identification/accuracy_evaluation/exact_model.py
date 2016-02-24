        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is possible  ###########
        ##################################################################################

import sumpf
import nlsp
import nlsp.common.plots as plot

def hgmwithfilter_evaluation(sweep_generator,branches,iden_method,Plot,Save):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    signal_start_freq = sweep_generator.GetStartFrequency()
    signal_stop_freq = sweep_generator.GetStopFrequency()
    signal_length = sweep_generator.GetLength()
    print signal_start_freq,signal_stop_freq,signal_length
    input_signal = sweep_generator.GetOutput()
    print len(input_signal)
    filter_spec_tofind = nlsp.log_bpfilter(signal_start_freq,signal_stop_freq,branches,input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec, nl_functions = iden_method(sweep_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print signal_length,len(ref_nlsystem.GetOutput())
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithoverlapfilter_evaluation(input_signal,branches,iden_method,Plot,Save):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and overlapping
                       bandpass filters as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    frequencies = [800,5000,900,5500,1000]
    signal_start_freq,signal_stop_freq,signal_length = input_signal.GetProperties()
    input_signal = input_signal.GetOutput()
    filter_spec_tofind = nlsp.create_bpfilter(frequencies,input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec, nl_functions = iden_method(input_signal,ref_nlsystem.GetOutput(),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def linearmodel_evaluation(input_signal,branches,iden_method,Plot,Save):
    """
    Evaluation of System Identification method by linear amplification
    nonlinear system - no nonlinearity, linear amplifier as linear system
    inputsignal - signal signal
    plot - the virtual linear system output and the identified linear system output
    expectation - utmost similarity between the two outputs
    """
    signal_start_freq,signal_stop_freq,signal_length = input_signal.GetProperties()
    input_signal = input_signal.GetOutput()
    amplification = 1.0
    ref_nlsystem = sumpf.modules.AmplifySignal(factor=amplification)
    ref_nlsystem.SetInput(input_signal)
    found_filter_spec, nl_functions = iden_method(input_signal,ref_nlsystem.GetOutput(),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                  nonlinear_functions=nl_functions,
                                                  filter_irs=found_filter_spec,
                                                  max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for linear systems: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithreversedfilter_evaluation(input_signal,branches,iden_method,Plot,Save):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    signal_start_freq,signal_stop_freq,signal_length = input_signal.GetProperties()
    print signal_start_freq,signal_stop_freq,signal_length
    input_signal = input_signal.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(signal_start_freq,signal_stop_freq,branches,input_signal)
    filter_spec_tofind = [i for i in reversed(filter_spec_tofind)]
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec, nl_functions = iden_method(input_signal,ref_nlsystem.GetOutput(),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print signal_length,len(ref_nlsystem.GetOutput())
    print "SNR between Reference and Identified output with reversed filter orders: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithamplifiedfilter_evaluation(input_signal,branches,iden_method,Plot,Save):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    signal_start_freq,signal_stop_freq,signal_length = input_signal.GetProperties()
    print signal_start_freq,signal_stop_freq,signal_length
    input_signal = input_signal.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(signal_start_freq,signal_stop_freq,branches,input_signal,amplify=True)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec, nl_functions = iden_method(input_signal,ref_nlsystem.GetOutput(),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print signal_length,len(ref_nlsystem.GetOutput())
    print "SNR between Reference and Identified output with differently amplified filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
