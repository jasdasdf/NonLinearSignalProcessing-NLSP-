import sumpf
import nlsp
import common.plot as plot

def sweep_evaluation():
    """
    Evaluation of Hammerstein group models using sweep
    Nonlinear system: hgm with same branch and same nl and linear functions
    input: sweep of certain length
    the SNR and MSE between the expected and identified output is evaluted
    """
    nlsystem_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics)
    nlsystem_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.01)
    nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                              filter_irs=filter_spec_tofind)
    nlsystem.SetInput(input_sweep)
    nlsystem_up.SetInput(input_sweep)
    nlsystem_lp.SetInput(input_sweep)
    found_filter_spec_up = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    hgm_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions,
                                              filter_irs=found_filter_spec_up,
                                              max_harmonics=max_harmonics)
    hgm_up.SetInput(input_sweep)
    found_filter_spec_lp = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    hgm_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions,
                                              filter_irs=found_filter_spec_lp,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.01)
    hgm_lp.SetInput(input_sweep)
    found_filter_spec = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    hgm = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                              filter_irs=found_filter_spec)
    hgm.SetInput(input_sweep)
    # plot.log()
    # plot.plot(sumpf.modules.FourierTransform(hgm.GetOutput()).GetSpectrum(), show=False)
    # plot.plot(sumpf.modules.FourierTransform(nlsystem.GetOutput()).GetSpectrum(), show=True)
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,simple: %r" \
          %(nlsp.get_snr(input_sweep,nlsystem.GetOutput()),
            nlsp.get_snr(input_sweep,hgm.GetOutput()),
            nlsp.get_snr(nlsystem.GetOutput(),hgm.GetOutput()))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,simple: %r" \
          %(nlsp.mean_squared_error(input_sweep,nlsystem.GetOutput()),
            nlsp.mean_squared_error(input_sweep,hgm.GetOutput()),
            nlsp.mean_squared_error(nlsystem.GetOutput(),hgm.GetOutput()))
    # plot.log()
    # plot.plot(sumpf.modules.FourierTransform(hgm_up.GetOutput()).GetSpectrum(), show=False)
    # plot.plot(sumpf.modules.FourierTransform(nlsystem_up.GetOutput()).GetSpectrum(), show=True)
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,upsample: %r" \
          %(nlsp.get_snr(input_sweep,nlsystem_up.GetOutput()),
            nlsp.get_snr(input_sweep,hgm_up.GetOutput()),
            nlsp.get_snr(nlsystem_up.GetOutput(),hgm_up.GetOutput()))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,upsample: %r" \
          %(nlsp.mean_squared_error(input_sweep,nlsystem_up.GetOutput()),
            nlsp.mean_squared_error(input_sweep,hgm_up.GetOutput()),
            nlsp.mean_squared_error(nlsystem_up.GetOutput(),hgm_up.GetOutput()))
    # plot.log()
    # plot.plot(sumpf.modules.FourierTransform(hgm_lp.GetOutput()).GetSpectrum(), show=False)
    # plot.plot(sumpf.modules.FourierTransform(nlsystem_lp.GetOutput()).GetSpectrum(), show=True)
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,lowpass: %r" \
          %(nlsp.get_snr(input_sweep,nlsystem_lp.GetOutput()),
            nlsp.get_snr(input_sweep,hgm_lp.GetOutput()),
            nlsp.get_snr(nlsystem_lp.GetOutput(),hgm_lp.GetOutput()))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,lowpass: %r" \
          %(nlsp.mean_squared_error(input_sweep,nlsystem_lp.GetOutput()),
            nlsp.mean_squared_error(input_sweep,hgm_lp.GetOutput()),
            nlsp.mean_squared_error(nlsystem_lp.GetOutput(),hgm_lp.GetOutput()))

def harmonics_evaluation():
    nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                              filter_irs=filter_spec_tofind)
    nlsystem_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics)
    nlsystem_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.01)
    nlsystem.SetInput(input_sweep)
    nlsystem_up.SetInput(input_sweep)
    nlsystem_lp.SetInput(input_sweep)
    found_filter_spec_up = nlsp.nonlinearconvolution_chebyshev_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    hgm_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions,
                                              filter_irs=found_filter_spec_up,
                                              max_harmonics=max_harmonics)
    hgm_up.SetInput(input_sweep)
    found_filter_spec_lp = nlsp.nonlinearconvolution_chebyshev_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    hgm_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions,
                                              filter_irs=found_filter_spec_lp,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.01)
    hgm_lp.SetInput(input_sweep)
    found_filter_spec = nlsp.nonlinearconvolution_chebyshev_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    hgm = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions,
                                              filter_irs=found_filter_spec)
    hgm.SetInput(input_sweep)
    plot.log()
    print "Simple hammerstein model harmonics plot"
    plot.plot(nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,branches),show=False)
    plot.plot(nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm.GetOutput(),sweep_start_freq,sweep_stop_freq,branches))
    print "Lowpass hammerstein model harmonics plot"
    plot.plot(nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem_lp.GetOutput(),sweep_start_freq,sweep_stop_freq,branches),show=False)
    plot.plot(nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm_lp.GetOutput(),sweep_start_freq,sweep_stop_freq,branches))
    print "Upsampling hammerstein model harmonics plot"
    plot.plot(nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem_up.GetOutput(),sweep_start_freq,sweep_stop_freq,branches),show=False)
    plot.plot(nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm_up.GetOutput(),sweep_start_freq,sweep_stop_freq,branches))

sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
branches = 5
sweep_length = 2**15
input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                               start_frequency=sweep_start_freq,
                                               stop_frequency=sweep_stop_freq).GetSignal()
nonlinear_functions = nlsp.nonlinearconvolution_powerseries_nlfunction(branches)
#nonlinear_functions = nlsp.nonlinearconvolution_chebyshev_nlfunction(branches)
#nonlinear_functions = [nlsp.function_factory.power_series(1),]*branches
#nonlinear_functions = [nlsp.function_factory.chebyshev1_polynomial(1),]*branches
#filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
filter_spec_tofind = [sumpf.modules.ImpulseGenerator(samplingrate=input_sweep.GetSamplingRate(),length=len(input_sweep)).GetSignal(),]*branches
max_harmonics = [1,2,3,4,5]
#max_harmonics = [1,]*branches

sweep_evaluation()
# harmonics_evaluation()