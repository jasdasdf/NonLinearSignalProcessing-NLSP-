        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is possible  ###########
        ##################################################################################

import sumpf
import nlsp
import nlsp.common.plots as plot

def audio_evaluation(input_generator,branches,iden_method,Plot):

    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.create_bpfilter([1000,2000,4000,8000,16000],input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    excitation = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Speech3.npz",
                                              format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    ref_nlsystem.SetInput(excitation)
    iden_nlsystem.SetInput(excitation)
    ref = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Ref",
                                      signal=ref_nlsystem.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    iden = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Iden",
                                      signal=iden_nlsystem.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithfilter_evaluation(input_generator,branches,iden_method,Plot):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_signal = input_generator.GetOutput()

    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    # sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/test_signals/Speech.npz", format=sumpf.modules.SignalFile.WAV_FLOAT)
    # ref_nlsystem.SetInput(sine.GetSignal())
    # iden_nlsystem.SetInput(sine.GetSignal())
    # for i in range(len(found_filter_spec)):
    #     plot.plot(sumpf.modules.FourierTransform(found_filter_spec[i]).GetSpectrum(),show=False)
    #     plot.plot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),show=False)
    # plot.show()
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithoverlapfilter_evaluation(input_generator,branches,iden_method,Plot):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and overlapping
                       bandpass filters as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    frequencies = [800,5000,900]
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.create_bpfilter(frequencies,input_signal)
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
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def linearmodel_evaluation(input_generator,branches,iden_method,Plot):
    """
    Evaluation of System Identification method by linear amplification
    nonlinear system - no nonlinearity, linear amplifier as linear system
    inputsignal - signal signal
    plot - the virtual linear system output and the identified linear system output
    expectation - utmost similarity between the two outputs
    """
    input_signal = input_generator.GetOutput()
    amplification = 1.0
    ref_nlsystem = sumpf.modules.AmplifySignal(factor=amplification)
    ref_nlsystem.SetInput(input_signal)

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for linear systems: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithreversedfilter_evaluation(input_generator,branches,iden_method,Plot):
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
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with reversed filter orders: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithamplifiedfilter_evaluation(input_generator,branches,iden_method,Plot):
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
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with differently amplified filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmallpass_evaluation(input_generator,branches,iden_method,Plot):
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
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output with differently amplified filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def novak_ieee_evaluation(input_generator,branches,iden_method,Plot):
    branches = 2
    input_signal = input_generator.GetOutput()
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(input_signal)
    hp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=10),
                                                       frequency=500.0,transform=True,resolution=prp.GetResolution(),
                                                       length=prp.GetSpectrumLength()).GetSpectrum()
    lp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=10),
                                                       frequency=1000.0,transform=False,resolution=prp.GetResolution(),
                                                       length=prp.GetSpectrumLength()).GetSpectrum()
    filter_spec_tofind = [sumpf.modules.InverseFourierTransform(hp).GetSignal(),
                          sumpf.modules.InverseFourierTransform(lp).GetSignal()]
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=[nlsp.function_factory.power_series(1),
                                                                      nlsp.function_factory.power_series(3)],
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,3))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,3))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def puretone_evaluation(input_generator,branches,iden_method,Plot):
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
    pure_tones = nlsp.generate_puretones([1000,5000,10000],input_signal.GetSamplingRate(),length=len(input_signal))
    ref_nlsystem.SetInput(pure_tones)
    iden_nlsystem.SetInput(pure_tones)
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output puretone: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def hgmwithfilter_evaluation_adaptive_chebyshev(input_generator,branches,iden_method,Plot):
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_signal = input_generator.GetOutput()

    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    outputs = []
    outputs.append(ref_nlsystem.GetOutput())
    for i in range(branches):
        input = nlsp.NonlinearFunction.chebyshev1_polynomial(i+1,signal=input_generator.GetOutput())
        ref_nlsystem.SetInput(input.GetOutput())
        outputs.append(ref_nlsystem.GetOutput())

    found_filter_spec, nl_functions = iden_method(input_generator,outputs,branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",show=False)
        plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",show=True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())