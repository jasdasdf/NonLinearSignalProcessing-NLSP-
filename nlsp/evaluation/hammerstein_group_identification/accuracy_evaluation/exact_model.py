        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is possible  ###########
        ##################################################################################

import sumpf
import nlsp
import nlsp.common.plots as plot

def hgmwithfilter_evaluation(input_generator,branches,nlfuntion,iden_method,Plot,reference=None):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_signal = input_generator.GetOutput()
    # filter_spec_tofind = nlsp.create_bpfilter([2000,8000,30000],input_signal)
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    length_kernel = len(filter_spec_tofind[0])
    # filter_spec_tofind = nlsp.log_chebyfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfuntion,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    found_filter_spec = nlsp.change_length_filterkernels(found_filter_spec,length=length_kernel)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    # nlsp.filterkernel_evaluation_plot(filter_spec_tofind,found_filter_spec)
    # nlsp.filterkernel_evaluation_sum(filter_spec_tofind,found_filter_spec)
    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem.SetInput(reference)
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithoverlapfilter_evaluation(input_generator,branches,nlfunction,iden_method,Plot,reference=None):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and overlapping
                       bandpass filters as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    frequencies = [500,3000,5000,7000,20000]
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.create_bpfilter(frequencies,input_signal)
    length_kernel = len(filter_spec_tofind[0])
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfunction,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    found_filter_spec = nlsp.change_length_filterkernels(found_filter_spec,length=length_kernel)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem.SetInput(reference)
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def linearmodel_evaluation(input_generator,branches,nlfunction,iden_method,Plot,reference=None):
    """
    Evaluation of System Identification method by linear amplification
    nonlinear system - no nonlinearity, linear amplifier as linear system
    inputsignal - signal signal
    plot - the virtual linear system output and the identified linear system output
    expectation - utmost similarity between the two outputs
    """
    input_signal = input_generator.GetOutput()
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(input_signal)
    filter_ir = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=10),
            frequency=10000.0,transform=False,resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
    ref_nlsystem = nlsp.AliasCompensatingHammersteinModelUpandDown(filter_impulseresponse=sumpf.modules.InverseFourierTransform(filter_ir).GetSignal())
    ref_nlsystem.SetInput(input_signal)

    # nonlinear system identification
    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    # linear system identification
    sweep = nlsp.NovakSweepGenerator_Sine(length=len(input_signal),sampling_rate=input_signal.GetSamplingRate())
    ref_nlsystem.SetInput(sweep.GetOutput())
    kernel_linear = nlsp.linear_identification_temporalreversal(sweep,ref_nlsystem.GetOutput())
    iden_linsystem = nlsp.AliasCompensatingHammersteinModelUpandDown(filter_impulseresponse=kernel_linear)

    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem.SetInput(reference)
        iden_linsystem.SetInput(reference)
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_linsystem.GetOutput()).GetSpectrum(),"Identified linear System",show=True)
    print "SNR between Reference and Identified output for linear systems: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
    print "SNR between Reference and Identified output for linear systems(linear identification): %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_linsystem.GetOutput())

def hgmwithreversedfilter_evaluation(input_generator,branches,nlfunction,iden_method,Plot,reference=None):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    filter_spec_tofind = [i for i in reversed(filter_spec_tofind)]
    length_kernel = len(filter_spec_tofind[0])
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfunction,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    found_filter_spec = nlsp.change_length_filterkernels(found_filter_spec,length=length_kernel)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem.SetInput(reference)
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with reversed filter orders: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithamplifiedfilter_evaluation(input_generator,branches,iden_method,Plot,reference=None):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal,amplify=True)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem.SetInput(reference)
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with differently amplified filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmallpass_evaluation(input_generator,branches,nlfunction,iden_method,Plot,reference=None):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and allpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_signal = input_generator.GetOutput()
    allpass = sumpf.modules.ImpulseGenerator(samplingrate=input_signal.GetSamplingRate(),length=len(input_signal)).GetSignal()
    filter_spec_tofind = [allpass,]*branches
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfunction,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem.SetInput(reference)
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with all pass filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())


def puretone_evaluation(input_generator,branches,iden_method,Plot,reference=None):
    input_signal = input_generator.GetOutput()

    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output sweep: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())
    pure_tones = nlsp.generate_puretones([200,1000,3000,5000,10000,20000],input_signal.GetSamplingRate(),length=len(input_signal))
    ref_nlsystem.SetInput(pure_tones)
    iden_nlsystem.SetInput(pure_tones)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output puretone: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithalphafilter_evaluation(input_generator,branches,nlfunction,iden_method,Plot,label=None,reference=None):
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.log_weightingfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfunction,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem.SetInput(reference)
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
    print "SNR between Reference and Identified output with weighted filtering: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

