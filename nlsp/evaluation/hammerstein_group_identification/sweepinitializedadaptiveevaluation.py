
import sumpf
import nlsp
import nlsp.common.plots as plot
import itertools
import time


sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**15
fade_out = 0.02
fade_in = 0.02
branches = 5
filter_length = 2**10
laplace = sumpf.modules.NoiseGenerator.LaplaceDistribution(mean=0.0,scale=0.2)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
wgn_laplace = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=laplace)

Plot = False
Save = False

input_generator = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)
nlfunction = nlsp.function_factory.legrendre_polynomial
reference = nlsp.RemoveOutliers(thresholds=[-1.0,1.0],value=0,signal=wgn_laplace.GetOutput())
reference = reference.GetOutput()

def hgmwithfilter_evaluation_sweepadaptive(input_generator,branches,nlfuntion,Plot,reference=None):
    input_signal = input_generator.GetOutput()
    # filter_spec_tofind = nlsp.create_bpfilter([2000,8000,30000],input_signal)
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    # filter_spec_tofind = nlsp.log_chebyfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfuntion,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
    ref_nlsystem.SetInput(sweep.GetOutput())
    sweep_start = time.clock()
    init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
    sweep_stop = time.clock()
    init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
    ref_nlsystem.SetInput(input_signal)
    adapt_sweep_start = time.clock()
    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(),
                                                                            branches=branches,
                                                                            init_coeffs=init_coeffs,
                                                                            filtertaps=filter_length)
    adapt_sweep_stop = time.clock()
    adapt_start = time.clock()
    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(),
                                                                            branches=branches,
                                                                            filtertaps=filter_length)
    adapt_stop = time.clock()
    print "sweep_identification time %r" %(sweep_start-sweep_stop)
    print "sweep_adapt_identification time %r" %(adapt_sweep_start-adapt_sweep_stop)
    print "adapt_identification time %r" %(adapt_start-adapt_stop)
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
hgmwithfilter_evaluation_sweepadaptive(input_generator,branches,nlfunction,Plot,reference)

def hgmwithoverlapfilter_evaluation(input_generator,branches,nlfunction,Plot,reference=None):
    frequencies = [500,3000,5000,7000,20000]
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.create_bpfilter(frequencies,input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfunction,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
    ref_nlsystem.SetInput(sweep.GetOutput())
    init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
    init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
    ref_nlsystem.SetInput(input_signal)
    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(),
                                                                            branches=branches,
                                                                            init_coeffs=init_coeffs)
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
hgmwithoverlapfilter_evaluation(input_generator,branches,nlfunction,Plot,reference)

def linearmodel_evaluation(input_generator,branches,nlfunction,Plot,reference=None):
    input_signal = input_generator.GetOutput()
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(input_signal)
    filter_ir = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=10),
            frequency=10000.0,transform=False,resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
    ref_nlsystem = nlsp.AliasCompensatingHammersteinModelUpandDown(filter_impulseresponse=sumpf.modules.InverseFourierTransform(filter_ir).GetSignal())

    sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
    ref_nlsystem.SetInput(sweep.GetOutput())
    init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
    init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
    ref_nlsystem.SetInput(input_signal)
    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(),
                                                                            branches=branches,
                                                                            init_coeffs=init_coeffs)
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
linearmodel_evaluation(input_generator,branches,nlfunction,Plot,reference)

def hgmwithreversedfilter_evaluation(input_generator,branches,nlfunction,Plot,reference=None):
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
    filter_spec_tofind = [i for i in reversed(filter_spec_tofind)]
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfunction,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
    ref_nlsystem.SetInput(sweep.GetOutput())
    init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
    init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
    ref_nlsystem.SetInput(input_signal)
    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(),
                                                                            branches=branches,
                                                                            init_coeffs=init_coeffs)

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
hgmwithreversedfilter_evaluation(input_generator,branches,nlfunction,Plot,reference)
def hgmallpass_evaluation(input_generator,branches,nlfunction,Plot,reference=None):
    input_signal = input_generator.GetOutput()
    allpass = sumpf.modules.ImpulseGenerator(samplingrate=input_signal.GetSamplingRate(),length=len(input_signal)).GetSignal()
    filter_spec_tofind = [allpass,]*branches
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfunction,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
    ref_nlsystem.SetInput(sweep.GetOutput())
    init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
    init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
    ref_nlsystem.SetInput(input_signal)
    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(),
                                                                            branches=branches,
                                                                            init_coeffs=init_coeffs)

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
hgmallpass_evaluation(input_generator,branches,nlfunction,Plot)
def hgmwithalphafilter_evaluation(input_generator,branches,nlfunction,Plot,label=None,reference=None):
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.log_weightingfilter(branches=branches,input=input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlfunction,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
    ref_nlsystem.SetInput(sweep.GetOutput())
    init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
    init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
    ref_nlsystem.SetInput(input_signal)
    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(),
                                                                            branches=branches,
                                                                            init_coeffs=init_coeffs)

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
hgmwithalphafilter_evaluation(input_generator,branches,nlfunction,Plot,reference)
def clippingHGMevaluation(input_generator,branches,Plot,reference=None):
    for t in range(8,11):
        t = t / 10.0
        thresholds = [-t,t]
        input_signal = input_generator.GetOutput()
        nl_functions = [nlsp.function_factory.hardclip(thresholds),]*branches
        filter_spec_tofind = nlsp.log_bpfilter(branches=branches, input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

        sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
        ref_nlsystem.SetInput(sweep.GetOutput())
        init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
        init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
        ref_nlsystem.SetInput(input_signal)
        found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                                outputs=ref_nlsystem.GetOutput(),
                                                                                branches=branches,
                                                                                init_coeffs=init_coeffs)

        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        # sine = sumpf.modules.SineWaveGenerator(frequency=5000.0,phase=0.0,samplingrate=input_signal.GetSamplingRate(),length=len(input_signal)).GetSignal()
        sine = sumpf.modules.SweepGenerator(samplingrate=input_signal.GetSamplingRate(),length=len(input_signal)).GetSignal()
        ref_nlsystem.SetInput(sine)
        iden_nlsystem.SetInput(sine)
        if reference is not None:
            reference = nlsp.change_length_signal(reference,length=len(input_signal))
            ref_nlsystem.SetInput(reference)
            iden_nlsystem.SetInput(reference)

        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=False)
        print "SNR between Reference and Identified output for symmetric hardclipping HGM(thresholds:%r): %r" %(thresholds,nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput()))
clippingHGMevaluation(input_generator,branches,Plot,reference)
def softclippingHGMevaluation(input_generator,branches,Plot,reference=None):
    for t in range(8,11):
        t = t / 10.0
        p = 1.0 - t
        input_signal = input_generator.GetOutput()
        nl_functions = [nlsp.function_factory.softclip(power=p),]*branches
        filter_spec_tofind = nlsp.log_bpfilter(branches=branches, input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

        sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
        ref_nlsystem.SetInput(sweep.GetOutput())
        init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
        init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
        ref_nlsystem.SetInput(input_signal)
        found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                                outputs=ref_nlsystem.GetOutput(),
                                                                                branches=branches,
                                                                                init_coeffs=init_coeffs)

        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        # sine = sumpf.modules.SineWaveGenerator(frequency=5000.0,phase=0.0,samplingrate=input_signal.GetSamplingRate(),length=len(input_signal)).GetSignal()
        sine = sumpf.modules.SweepGenerator(samplingrate=input_signal.GetSamplingRate(),length=len(input_signal)).GetSignal()
        ref_nlsystem.SetInput(sine)
        iden_nlsystem.SetInput(sine)
        if reference is not None:
            reference = nlsp.change_length_signal(reference,length=len(input_signal))
            ref_nlsystem.SetInput(reference)
            iden_nlsystem.SetInput(reference)

        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=False)
        print "SNR between Reference and Identified output for symmetric hardclipping HGM(threshold:%r): %r" %(t,nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput()))
softclippingHGMevaluation(input_generator,branches,Plot,reference)
def doublehgm_same_evaluation(input_generator,branches,Plot,reference=None):
    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)


    sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=sweep.GetOutput(),
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.power_series,branches)),
                                                filter_irs=(filter_spec_tofind,filter_spec_tofind),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))

    init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(2),branches=branches)
    init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=input_signal,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.power_series,branches)),
                                                filter_irs=(filter_spec_tofind,filter_spec_tofind),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))

    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(2),
                                                                            branches=branches,
                                                                            init_coeffs=init_coeffs)

    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=reference,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.power_series,branches)),
                                                filter_irs=(filter_spec_tofind,filter_spec_tofind),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput(2)).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for double hgm all same: %r" %nlsp.snr(ref_nlsystem.GetOutput(2),
                                                                                             iden_nlsystem.GetOutput())
doublehgm_same_evaluation(input_generator,branches,Plot,reference)
def doublehgm_different_evaluation(input_generator,branches,Plot,reference=None):
    input_signal = input_generator.GetOutput()
    filter_spec_tofind1 = nlsp.log_bpfilter(branches=branches, input=input_signal)
    filter_spec_tofind2 = nlsp.log_chebyfilter(branches=branches, input=input_signal)

    sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=sweep.GetOutput(),
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)),
                                                filter_irs=(filter_spec_tofind1,filter_spec_tofind2),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))
    init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(2),branches=branches)
    init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
    ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=input_signal,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)),
                                                filter_irs=(filter_spec_tofind1,filter_spec_tofind2),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))
    found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                            outputs=ref_nlsystem.GetOutput(2),
                                                                            branches=branches,
                                                                            init_coeffs=init_coeffs)

    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if reference is not None:
        reference = nlsp.change_length_signal(reference,length=len(input_signal))
        ref_nlsystem = nlsp.HammersteinGroup_Series(input_signal=reference,
                                                nonlinear_functions=(nlsp.nl_branches(nlsp.function_factory.power_series,branches),nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)),
                                                filter_irs=(filter_spec_tofind1,filter_spec_tofind2),
                                                max_harmonics=(range(1,branches+1),range(1,branches+1)),
                                                hgm_type=(nlsp.HammersteinGroupModel_up,nlsp.HammersteinGroupModel_up))
        iden_nlsystem.SetInput(reference)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput(2)).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output for double hgm different: %r" %nlsp.snr(ref_nlsystem.GetOutput(2),
                                                                                             iden_nlsystem.GetOutput())
doublehgm_different_evaluation(input_generator,branches,Plot,reference)
def differentlength_evaluation(input_generator,branches,Plot,reference=None):
    length_ref = [2**15,2**16,2**17]
    length_iden = [2**15,2**16,2**17]
    input_generator_ref = input_generator
    input_generator_iden = input_generator
    for signal_length, ref_length in zip(length_iden,length_ref):
        input_generator_ref.SetLength(ref_length)
        input_ref = input_generator_ref.GetOutput()
        filter_spec_tofind = nlsp.log_weightingfilter(branches=branches,input=input_ref)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_ref,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))

        sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_ref.GetSamplingRate(), length=len(input_ref))
        ref_nlsystem.SetInput(sweep.GetOutput())
        init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
        init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
        ref_nlsystem.SetInput(input_ref)
        found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator_ref,
                                                                                outputs=ref_nlsystem.GetOutput(),
                                                                                branches=branches,
                                                                                init_coeffs=init_coeffs)

        input_generator_iden.SetLength(signal_length)
        input_iden = input_generator_iden.GetOutput()
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_iden,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        if reference is not None:
            reference = nlsp.change_length_signal(reference,length=len(input_ref))
            ref_nlsystem.SetInput(reference)
            iden_nlsystem.SetInput(reference)

        if Plot is True:
            plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
            plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        print "SNR between Reference(length:%r) and Identified output(length:%r) : %r" %(len(input_ref),len(input_iden),nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                     iden_nlsystem.GetOutput()))
differentlength_evaluation(input_generator,branches,Plot,reference)
def differentbranches_evaluation(input_generator,branches,Plot,reference=None):
    ref_branches = 3
    for branches in range(1,branches):
        input_signal = input_generator.GetOutput()

        filter_spec_tofind = nlsp.log_weightingfilter(branches=ref_branches,input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,ref_branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,ref_branches+1))

        sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
        ref_nlsystem.SetInput(sweep.GetOutput())
        init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
        init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
        ref_nlsystem.SetInput(input_signal)
        found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                                outputs=ref_nlsystem.GetOutput(),
                                                                                branches=branches,
                                                                                init_coeffs=init_coeffs)

        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        if reference is not None:
            reference = nlsp.change_length_signal(reference,length=len(input_signal))
            ref_nlsystem.SetInput(reference)
            iden_nlsystem.SetInput(reference)
        if Plot is True:
            plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
            plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        print "SNR between Reference and Identified output : %r, with number of ref_branches: %r and iden_branches: %r" %(nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                     iden_nlsystem.GetOutput()),ref_branches,branches)

differentbranches_evaluation(input_generator,branches,Plot,reference)
def robustness_excitation_evaluation(input_generator,branches,Plot,reference=None):

    excitation_signal_amp = [0.5,1.0]
    sample_signal_amp = [0.5,1.0,2.0]
    input = input_generator.GetOutput()
    for excitation_amp,sample_amp in itertools.product(excitation_signal_amp,sample_signal_amp):
        input_signal = sumpf.modules.AmplifySignal(input=input,factor=excitation_amp).GetOutput()
        sample_signal = nlsp.WhiteGaussianGenerator(sampling_rate=input_signal.GetSamplingRate(),length=len(input_signal),
                                                    distribution=sumpf.modules.NoiseGenerator.UniformDistribution(minimum=-sample_amp,maximum=sample_amp))
        sample_signal = sample_signal.GetOutput()
        filter_spec_tofind = nlsp.log_weightingfilter(branches=branches,input=input_signal)
        ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                     nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                     filter_irs=filter_spec_tofind,
                                                     max_harmonics=range(1,branches+1))
        sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=input_signal.GetSamplingRate(), length=len(input_signal))
        ref_nlsystem.SetInput(sweep.GetOutput())
        init_coeffs, non = nlsp.nonlinearconvolution_powerseries_temporalreversal(sweep,ref_nlsystem.GetOutput(),branches=branches)
        init_coeffs = nlsp.change_length_filterkernels(init_coeffs,filter_length)
        ref_nlsystem.SetInput(input_signal)
        found_filter_spec, nl_functions = nlsp.adaptive_identification_legendre(input_generator=input_generator,
                                                                                outputs=ref_nlsystem.GetOutput(),
                                                                                branches=branches,
                                                                                init_coeffs=init_coeffs)
        iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=sample_signal,
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        ref_nlsystem.SetInput(sample_signal)
        if Plot is True:
            nlsp.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output Scaled",False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        print "SNR between Scaled Identified with(amp:%r) and Tested with(amp:%r) output: %r" %(excitation_amp,sample_amp,nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                                 iden_nlsystem.GetOutput()))

robustness_excitation_evaluation(input_generator,branches,Plot,reference)