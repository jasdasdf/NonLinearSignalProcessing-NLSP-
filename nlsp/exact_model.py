        ##################################################################################
        #####   Evaluation of Nonlinear systems where Exact model is possible  ###########
        ##################################################################################

import sumpf
import nlsp
import common.plot as plot

def hgmwithfilter_wgn_evaluation():
    """
    Evaluation of System Identification method by hgm virtual nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                        as linear functions
    inputsignal - white gaussian noise signal
    plot - the original filter spectrum and the identified filter spectrum, the reference output and identified output
    expectation - utmost similarity between the two spectrums
    """
    input_wgn = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0),
                                             samplingrate=sampling_rate,length=wgn_length).GetSignal()
    filter_spec_tofind = nlsp.log_bpfilter(50.0,20000.0,branches,input_wgn)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_wgn,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec = nlsp.wgn_hgm_identification(input_wgn,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel(input_signal=input_wgn,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    if Plot is True:
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference Output",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified Output",True)
        for i,foundspec in enumerate(found_filter_spec):
            nlsp.relabelandplot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),str(i+1)+str(" filter,identified"),False)
            nlsp.relabelandplot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),str(i+1)+str(" filter,input"),False)
        plot.show()
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.signal_to_noise_ratio_time(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

sampling_rate = 48000.0
branches = 3
wgn_length = 2**8
Plot = True

hgmwithfilter_wgn_evaluation()
