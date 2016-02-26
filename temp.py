        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is possible  ###########
        ##################################################################################

import sumpf
import nlsp
import nlsp.common.plots as plot
import numpy

def hgmwithfilter_wgn_evaluation():
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    inputsignal - white gaussian noise signal
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_wgn = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=0.5),
                                             samplingrate=sampling_rate,length=wgn_length).GetSignal()
    input_wgn_freq = sumpf.modules.FourierTransform(input_wgn).GetSpectrum()
    bp = sumpf.modules.RectangleFilterGenerator(resolution=input_wgn_freq.GetResolution(),length=len(input_wgn_freq)).GetSpectrum()
    bp_out = sumpf.modules.MultiplySpectrums(spectrum1=input_wgn_freq,spectrum2=bp).GetOutput()
    input_wgn = sumpf.modules.InverseFourierTransform(bp_out).GetSignal()
    filter_spec_tofind = nlsp.log_bpfilter(50.0,20000.0,branches,input_wgn)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_wgn,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec = nlsp.wgn_hgm_identification(input_wgn,ref_nlsystem.GetOutput(),branches)
    print len(found_filter_spec),type(found_filter_spec),found_filter_spec[0]
    iden_nlsystem = nlsp.HammersteinGroupModel(input_signal=input_wgn,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

sampling_rate = 48000.0
branches = 5
wgn_length = 2**15
Plot = True

# hgmwithfilter_wgn_evaluation()


def generateandevaluate():
    start_freq = 10.0
    stop_freq = 23000.0
    sampling_rate = 48000.0
    fade_out = 0.01
    fade_in = 0.01
    length = [2**16,2**18,2**20]
    sweep = "262144"
    sweep_gen = nlsp.NovakSweepGenerator(sampling_rate=sampling_rate, length=2**18, start_frequency=start_freq,
                                     stop_frequency=stop_freq ,fade_out= fade_out,fade_in=fade_in)
    excitation = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/recordings/inputs/%s"%sweep,
                                          format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    response = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/recordings/outputs/%s"%sweep,
                                          format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    response = sumpf.modules.SplitSignal(response,channels=[1]).GetOutput()
    nlsp.plot(sumpf.modules.FourierTransform(excitation).GetSpectrum())
    nlsp.plot(sumpf.modules.FourierTransform(response).GetSpectrum())

# generateandevaluate()
