import sumpf
import common.plot as plot
import math
import sympy
from sympy import Symbol
from sympy.solvers import solve
import nlsp
import numpy

def findfilter_evaluation():
    """
    Evaluation of System Identification method by hgm nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters as
                       linear functions
    inputsignal - sweep signal
    plot - the original filter spectrum and the identified filter spectrum
    expectation - utmost similarity between the two spectrums
    """
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                               start_frequency=sweep_start_freq,
                                               stop_frequency=sweep_stop_freq).GetSignal()
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSignal(input_sweep)
    filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
    nlsystem = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=range(1,branches+1))
    nlsystem.SetInput(input_sweep)
    # found_filter_spec = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
    #                                                                                                  sweep_stop_freq,
    #                                                                                                  branches])
    iden = nlsp.NLConvolution(input_sweep,nlsystem.GetOutput())
    found_filter_power_1 = iden.GetPower_filter_1()
    found_filter_power_2 = iden.GetPower_filter_2()
    found_filter_power_auto = iden.GetPower_filter_auto()
    found_filter_spec_cheby = iden.GetCheby_filter()
    # for i in range(0,len(found_filter_power_1)):
    #     plot.log()
    #     plot.plot(sumpf.modules.FourierTransform(found_filter_power_1[i]).GetSpectrum(),show=False)
    #     plot.plot(sumpf.modules.FourierTransform(found_filter_power_2[i]).GetSpectrum(),show=False)
    #     plot.plot(sumpf.modules.FourierTransform(found_filter_power_auto[i]).GetSpectrum(),show=False)
    #     plot.plot(sumpf.modules.FourierTransform(found_filter_spec_cheby[i]).GetSpectrum(),show=False)
    #     # plot.plot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),show=False)
    #     plot.show()

sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
sweep_length = 2**13
branches = 5
sampling_rate = 48000

findfilter_evaluation()