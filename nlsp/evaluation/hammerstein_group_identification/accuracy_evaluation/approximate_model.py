        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is not possible  #######
        ##################################################################################

import itertools
import sumpf
import nlsp
import nlsp.common.plots as plot

def symmetric_hardclipping_evaluation(input_generator,branches,iden_method,Plot):
    """
    Evaluation of System Identification method by hard clipping system
    nonlinear system - virtual clipping systems which hard clips the signal amplitute which are not in the threshold range
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    for t in range(8,11):
        t = t / 10.0
        thresholds = [-t,t]
        input_signal = input_generator.GetOutput()
        ref_nlsystem = sumpf.modules.ClipSignal(thresholds=thresholds)
        ref_nlsystem.SetInput(input_signal)

        found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        sine = sumpf.modules.SineWaveGenerator(frequency=1000.0,phase=0.0,samplingrate=input_signal.GetSamplingRate(),length=len(input_signal)).GetSignal()
        ref_nlsystem.SetInput(sine)
        iden_nlsystem.SetInput(sine)
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=False)
        print "SNR between Reference and Identified output for symmetric hardclipping(thresholds:%r): %r" %(thresholds,nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput()))

def nonsymmetric_hardclipping_evaluation(input_generator,branches,iden_method,Plot):
    """
    Evaluation of System Identification method by hard clipping system
    nonlinear system - virtual clipping systems which hard clips the signal amplitute which are not in the threshold range
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    t1 = range(8,11)
    t2 = range(8,11)
    for th1, th2 in itertools.product(t1, t2):
        th1 = th1 / 10.0
        th2 = th2 / 10.0
        thresholds = [-th1,th2]
        input_signal = input_generator.GetOutput()
        ref_nlsystem = sumpf.modules.ClipSignal(thresholds=thresholds)
        ref_nlsystem.SetInput(input_signal)

        found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        sine = sumpf.modules.SineWaveGenerator(frequency=1000.0,phase=0.0,samplingrate=input_signal.GetSamplingRate(),length=len(input_signal)).GetSignal()
        ref_nlsystem.SetInput(sine)
        iden_nlsystem.SetInput(sine)
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=False)
        print "SNR between Reference and Identified output for non symmetric hardclipping(thresholds:%r): %r" %(thresholds,nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput()))

def softclipping_evaluation(input_generator,branches,iden_method,Plot):
    """
    Evaluation of System Identification method by soft clipping system
    nonlinear system - virtual clipping systems which soft clips the signal amplitute which are not in the threshold range
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    thresholds = [-1.0,1.0]
    power = 1.0/3.0
    input_signal = input_generator.GetOutput()
    ref_nlsystem = nlsp.NLClipSignal(thresholds=thresholds, power=power)
    ref_nlsystem.SetInput(input_signal)

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for soft clipping: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
def doublehgm_same_evaluation(input_generator,branches,iden_method,Plot):
    """
    Evaluation of System Identification method by double hgm virtual nl system with same nonlinear degree and filters
    nonlinear system - two virtual hammerstein group model with power series polynomials as nl function and bandpass
                        filters as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=input_signal,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.power_series,branches)),
                                                filter_irs=(filter_spec_tofind,filter_spec_tofind),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(2),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput(2)).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for double hgm all same: %r" %nlsp.snr(ref_nlsystem.GetOutput(2),
                                                                                             iden_nlsystem.GetOutput())

def doublehgm_samenl_evaluation(input_generator,branches,iden_method,Plot):
    input_signal = input_generator.GetOutput()
    filter_spec_tofind1 = nlsp.log_bpfilter(branches=branches, input=input_signal)
    filter_spec_tofind2 = nlsp.log_chebyfilter(branches=branches, input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=input_signal,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.power_series,branches)),
                                                filter_irs=(filter_spec_tofind1,filter_spec_tofind2),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(2),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput(2)).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for double hgm same nl: %r" %nlsp.snr(ref_nlsystem.GetOutput(2),
                                                                                             iden_nlsystem.GetOutput())

def doublehgm_samefilter_evaluation(input_generator,branches,iden_method,Plot):
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches, input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=input_signal,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)),
                                                filter_irs=(filter_spec_tofind,filter_spec_tofind),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(2),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput(2)).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for double hgm same filter: %r" %nlsp.snr(ref_nlsystem.GetOutput(2),
                                                                                             iden_nlsystem.GetOutput())

def doublehgm_different_evaluation(input_generator,branches,iden_method,Plot):
    input_signal = input_generator.GetOutput()
    filter_spec_tofind1 = nlsp.log_bpfilter(branches=branches, input=input_signal)
    filter_spec_tofind2 = nlsp.log_chebyfilter(branches=branches, input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=input_signal,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)),
                                                filter_irs=(filter_spec_tofind1,filter_spec_tofind2),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(2),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput(2)).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for double hgm same nl: %r" %nlsp.snr(ref_nlsystem.GetOutput(2),
                                                                                             iden_nlsystem.GetOutput())