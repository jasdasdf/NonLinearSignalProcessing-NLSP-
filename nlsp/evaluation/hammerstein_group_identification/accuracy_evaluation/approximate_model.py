        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is not possible  #######
        ##################################################################################

import sumpf
import nlsp
import nlsp.common.plots as plot

def hardclipping_evaluation(input_signal,branches,iden_method,Plot,Save):
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
    found_filter_spec, nl_functions = iden_method(input_signal,ref_nlsystem.GetOutput(),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                  nonlinear_functions=nl_functions,
                                                  filter_irs=found_filter_spec,
                                                  max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for hardclipping: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def softclipping_evaluation(input_signal,branches,iden_method,Plot,Save):
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
    found_filter_spec, nl_functions = iden_method(input_signal,ref_nlsystem.GetOutput(),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                  nonlinear_functions=nl_functions,
                                                  filter_irs=found_filter_spec,
                                                  max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for soft clipping: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
def doublehgm_same_evaluation(input_signal,branches,iden_method,Plot,Save):
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
    found_filter_spec, nl_functions = iden_method(input_signal,ref_nlsystem.GetOutput(2),signal_start_freq,signal_stop_freq,
                                        signal_length,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput(2)).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for double hgm: %r" %nlsp.snr(ref_nlsystem.GetOutput(2),
                                                                                             iden_nlsystem.GetOutput())
