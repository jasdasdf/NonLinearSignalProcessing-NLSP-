        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is not possible  #######
        ##################################################################################

import sumpf
import nlsp
import common.plot as plot

def hardclipping_evaluation(input_signal,branches,Plot,iden_method):
    """
    Evaluation of System Identification method by hard clipping system
    nonlinear system - virtual clipping systems which hard clips the signal amplitute which are not in the threshold range
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    thresholds = [-0.7,0.7]
    signal_start_freq,signal_stop_freq,signal_length = input_signal.GetProperties()
    input_signal = input_signal.GetOutput()
    ref_nlsystem = sumpf.modules.ClipSignal(thresholds=thresholds)
    ref_nlsystem.SetInput(input_signal)
    found_filter_spec = iden_method(input_signal,ref_nlsystem.GetOutput(),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                  nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=found_filter_spec,
                                                  max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
    print "SNR between Reference and Identified output for hardclipping: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def softclipping_evaluation(input_signal,branches,Plot,iden_method):
    """
    Evaluation of System Identification method by soft clipping system
    nonlinear system - virtual clipping systems which soft clips the signal amplitute which are not in the threshold range
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    thresholds = [-1.0,1.0]
    power = 1.0/3.0
    signal_start_freq,signal_stop_freq,signal_length = input_signal.GetProperties()
    input_signal = input_signal.GetOutput()
    ref_nlsystem = nlsp.NLClipSignal(thresholds=thresholds, power=power)
    ref_nlsystem.SetInput(input_signal)
    found_filter_spec = iden_method(input_signal,ref_nlsystem.GetOutput(),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                  nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=found_filter_spec,
                                                  max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
    print "SNR between Reference and Identified output for soft clipping: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
def doublehgm_same_evaluation(input_signal,branches,Plot,iden_method):
    """
    Evaluation of System Identification method by double hgm virtual nl system with same nonlinear degree and filters
    nonlinear system - two virtual hammerstein group model with power series polynomials as nl function and bandpass
                        filters as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    signal_start_freq,signal_stop_freq,signal_length = input_signal.GetProperties()
    input_signal = input_signal.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(signal_start_freq,signal_stop_freq,branches,input_signal)
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=input_signal,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,5),nlsp.nl_branches(nlsp.function_factory.power_series,5)),
                                                filter_irs=(filter_spec_tofind,filter_spec_tofind),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))
    found_filter_spec = iden_method(input_signal,ref_nlsystem.GetOutput(2),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,5),
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput(2)).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        plot.log()
        for i,foundspec in enumerate(found_filter_spec):
            nlsp.relabelandplot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),str(i+1)+str(" filter,input"),False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),str(i+1)+str(" filter,identified"),False)
        plot.show()
    print "SNR between Reference and Identified output for double hgm: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(2),
                                                                                             iden_nlsystem.GetOutput())
