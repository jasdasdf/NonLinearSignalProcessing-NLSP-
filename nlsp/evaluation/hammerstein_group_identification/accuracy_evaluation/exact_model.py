        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is possible  ###########
        ##################################################################################

import sumpf
import nlsp
import nlsp.common.plots as plot

def hgmwithfilter_evaluation(input_signal,branches,iden_method,Plot,Save):
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
    nlsp.plot_groupdelayandmagnitude(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),show=False)
    nlsp.plot_groupdelayandmagnitude(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),show=True)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False,save=Save,name="filter")
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        for i,foundspec in enumerate(found_filter_spec):
            nlsp.relabelandplot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),str(i+1)+str(" filter,input"),False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),str(i+1)+str(" filter,identified"),False)
        plot.show()
    print signal_length,len(ref_nlsystem.GetOutput())
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithoverlapfilter_evaluation(input_signal,branches,iden_method,Plot,Save):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and overlapping
                       bandpass filters as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    frequencies = [800,1000,1500,2000,2500]
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
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        for i,foundspec in enumerate(found_filter_spec):
            nlsp.relabelandplot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),str(i+1)+str(" filter,input"),False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),str(i+1)+str(" filter,identified"),False)
        plot.show()
    print "SNR between Reference and Identified output with overlapping filters: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
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
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
    print "SNR between Reference and Identified output with overlapping filters: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

