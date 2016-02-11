        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is not possible  #######
        ##################################################################################

import sumpf
import nlsp
import common.plot as plot

def hardclipping_evaluation():
    """
    Evaluation of System Identification method by hard clipping system
    nonlinear system - virtual clipping systems which hard clips the signal amplitute which are not in the threshold range
    inputsignal - sweep signal
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    thresholds = [-0.7,0.7]
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length).GetSignal()
    ref_nlsystem = sumpf.modules.ClipSignal(thresholds=thresholds)
    ref_nlsystem.SetInput(input_sweep)
    identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,
                                        len(input_sweep),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                  nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=identification.GetPower_filter_1(),
                                                  max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
    print "SNR between Reference and Identified output for hardclipping: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def softclipping_evaluation():
    """
    Evaluation of System Identification method by soft clipping system
    nonlinear system - virtual clipping systems which soft clips the signal amplitute which are not in the threshold range
    inputsignal - sweep signal
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    thresholds = [-1.0,1.0]
    power = 1.0/3.0
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length).GetSignal()
    ref_nlsystem = nlsp.NLClipSignal(thresholds=thresholds, power=power)
    ref_nlsystem.SetInput(input_sweep)
    identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,
                                        len(input_sweep),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                                  nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                  filter_irs=identification.GetPower_filter_1(),
                                                  max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
    print "SNR between Reference and Identified output for soft clipping: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
def doublehgm_same_evaluation():
    """
    Evaluation of System Identification method by double hgm virtual nl system with same nonlinear degree and filters
    nonlinear system - two virtual hammerstein group model with power series polynomials as nl function and bandpass
                        filters as linear functions
    inputsignal - sweep signal
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                               start_frequency=sweep_start_freq,
                                               stop_frequency=sweep_stop_freq).GetSignal()
    filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=input_sweep,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,5),nlsp.nl_branches(nlsp.function_factory.power_series,5)),
                                                filter_irs=(filter_spec_tofind,filter_spec_tofind),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))
    identification = nlsp.NLConvolution(input_sweep,ref_nlsystem.GetOutput(2),sweep_start_freq,sweep_stop_freq,
                                        len(input_sweep),branches)
    found_filter_spec = identification.GetPower_filter_1()
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
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

sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
branches = 5
sweep_length = 2**15
Plot = True

hardclipping_evaluation()
softclipping_evaluation()
doublehgm_same_evaluation()