import sumpf
import nlsp
import common.plot as plot

def sweep_evaluation_power():
    """
    Evaluation of Hammerstein group models using sweep
    Nonlinear system: hgm with same branch and same nl and linear functions
    input: sweep of certain length
    the SNR and MSE between the expected and identified output is evaluated
    """
    # virtual nonlinear systems for evaluation
    # nlsystem = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions_power,
    #                                           filter_irs=filter_spec_tofind,
    #                                           max_harmonics=max_harmonics)
    nlsystem = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.01)
    # nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions_power,
    #                                           filter_irs=filter_spec_tofind)
    nlsystem.SetInput(input_sweep)

    # system identification of the nonlinear system
    found_filter_spec = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])

    # construct hammerstein group model from identified parameters
    hgm_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=found_filter_spec,
                                              max_harmonics=max_harmonics)
    hgm_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=found_filter_spec,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.01)
    hgm = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=found_filter_spec)
    hgm_up.SetInput(input_sweep)
    hgm.SetInput(input_sweep)
    hgm_lp.SetInput(input_sweep)

    # print the mean square error value
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,simple: %r" \
          %(nlsp.signal_to_noise_ratio_freq_range(input_sweep,nlsystem.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(input_sweep,hgm.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(nlsystem.GetOutput(),hgm.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,simple: %r" \
          %(nlsp.signal_to_noise_ratio_freq_rangesignal_to_noise_ratio_freq_range(input_sweep,nlsystem.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(input_sweep,hgm.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(nlsystem.GetOutput(),hgm.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]))
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,upsample: %r" \
          %(nlsp.signal_to_noise_ratio_freq_range(input_sweep,nlsystem.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(input_sweep,hgm_up.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(nlsystem.GetOutput(),hgm_up.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,upsample: %r" \
          %(nlsp.signal_to_noise_ratio_freq_range(input_sweep,nlsystem.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(input_sweep,hgm_up.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(nlsystem.GetOutput(),hgm_up.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]))
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,lowpass: %r" \
          %(nlsp.signal_to_noise_ratio_freq_range(input_sweep,nlsystem.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(input_sweep,hgm_lp.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(nlsystem.GetOutput(),hgm_lp.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,lowpass: %r" \
          %(nlsp.signal_to_noise_ratio_freq_range(input_sweep,nlsystem.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(input_sweep,hgm_lp.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]),
            nlsp.signal_to_noise_ratio_freq_range(nlsystem.GetOutput(),hgm_lp.GetOutput(),[sweep_start_freq+100,sweep_stop_freq-100]))


    # plot.log()
    # plot.plot(sumpf.modules.FourierTransform(hgm.GetOutput()).GetSpectrum(), show=False)
    # plot.plot(sumpf.modules.FourierTransform(nlsystem.GetOutput()).GetSpectrum(), show=True)
    # plot.log()
    # plot.plot(sumpf.modules.FourierTransform(hgm_up.GetOutput()).GetSpectrum(), show=False)
    # plot.plot(sumpf.modules.FourierTransform(nlsystem_up.GetOutput()).GetSpectrum(), show=True)
    # plot.log()
    # plot.plot(sumpf.modules.FourierTransform(hgm_lp.GetOutput()).GetSpectrum(), show=False)
    # plot.plot(sumpf.modules.FourierTransform(nlsystem_lp.GetOutput()).GetSpectrum(), show=True)

sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
branches = 5
sweep_length = 2**18
input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                               start_frequency=sweep_start_freq,
                                               stop_frequency=sweep_stop_freq).GetSignal()

# Nonlinear functions
nonlinear_functions_power = nlsp.nonlinearconvolution_powerseries_nlfunction(branches)
#nonlinear_functions_chebyshev = nlsp.nonlinearconvolution_chebyshev_nlfunction(branches)
#nonlinear_functions_power = [nlsp.function_factory.power_series(1),]*branches
#nonlinear_functions_chebyshev = [nlsp.function_factory.chebyshev1_polynomial(1),]*branches

# Filter Specifications
filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
# filter_spec_tofind = [sumpf.modules.ImpulseGenerator(samplingrate=input_sweep.GetSamplingRate(),length=len(input_sweep)).GetSignal(),]*branches

# Max harmonics
max_harmonics = [1,2,3,4,5]
#max_harmonics = [1,]*branches

sweep_evaluation_power()