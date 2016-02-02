import sumpf
import nlsp
import common.plot as plot

def harmonics_difference_powerseries_evaluation():

    # the nonlinear reference system
    nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=filter_spec_tofind)
    nlsystem_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics)
    nlsystem_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.0001)
    nlsystem.SetInput(input_sweep)
    nlsystem_up.SetInput(input_sweep)
    nlsystem_lp.SetInput(input_sweep)

    # identification method to find the nonlinear system parameters
    found_filter_spec = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    found_filter_spec_up = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    found_filter_spec_lp = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])

    # construct hgm using identified parameters
    hgm_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=found_filter_spec_up,
                                              max_harmonics=max_harmonics)
    hgm_up.SetInput(input_sweep)
    hgm_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=found_filter_spec_lp,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.0001)
    hgm_lp.SetInput(input_sweep)
    hgm = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions_power,
                                              filter_irs=found_filter_spec)
    hgm.SetInput(input_sweep)

    # calculate the harmonics from the input and output using helper function
    hgm_harmonics =  nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    hgm_lp_harmonics =  nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm_lp.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    hgm_up_harmonics =  nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm_up.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    nlsystem_harmonics = nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    nlsystem_lp_harmonics = nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem_lp.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    nlsystem_up_harmonics = nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem_up.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)

    # calculate the difference between the observed and identified harmonics
    simple_hgm_diff = nlsp.cut_spectrum(hgm_harmonics - nlsystem_harmonics,[100,19900])
    lp_hgm_diff = nlsp.cut_spectrum(hgm_lp_harmonics - nlsystem_lp_harmonics,[100,19900])
    up_hgm_diff = nlsp.cut_spectrum(hgm_up_harmonics - nlsystem_up_harmonics,[100,19900])


    # plot the difference
    plot.log()
    print "Simple hammerstein model harmonics plot"
    plot.plot(simple_hgm_diff)
    print "Lowpass hammerstein model harmonics plot"
    plot.plot(lp_hgm_diff)
    print "Upsampling hammerstein model harmonics plot"
    plot.plot(up_hgm_diff)

def harmonics_difference_chebyshev_evaluation():

    # the nonlinear reference system
    nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions_chebyshev,
                                              filter_irs=filter_spec_tofind)
    nlsystem_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions_chebyshev,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics)
    nlsystem_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions_chebyshev,
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.0001)
    nlsystem.SetInput(input_sweep)
    nlsystem_up.SetInput(input_sweep)
    nlsystem_lp.SetInput(input_sweep)

    # identification method to find the nonlinear system parameters
    found_filter_spec = nlsp.nonlinearconvolution_chebyshev_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    found_filter_spec_up = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    found_filter_spec_lp = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])

    # construct hgm using identified parameters
    hgm_up = nlsp.HammersteinGroupModel_up(nonlinear_functions=nonlinear_functions_chebyshev,
                                              filter_irs=found_filter_spec_up,
                                              max_harmonics=max_harmonics)
    hgm_up.SetInput(input_sweep)
    hgm_lp = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nonlinear_functions_chebyshev,
                                              filter_irs=found_filter_spec_lp,
                                              max_harmonics=max_harmonics,
                                              filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                              attenuation=0.0001)
    hgm_lp.SetInput(input_sweep)
    hgm = nlsp.HammersteinGroupModel(nonlinear_functions=nonlinear_functions_chebyshev,
                                              filter_irs=found_filter_spec)
    hgm.SetInput(input_sweep)

    # calculate the harmonics from the input and output using helper function
    hgm_harmonics =  nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    hgm_lp_harmonics =  nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm_lp.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    hgm_up_harmonics =  nlsp.get_sweep_harmonics_spectrum(input_sweep,hgm_up.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    nlsystem_harmonics = nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    nlsystem_lp_harmonics = nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem_lp.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)
    nlsystem_up_harmonics = nlsp.get_sweep_harmonics_spectrum(input_sweep,nlsystem_up.GetOutput(),sweep_start_freq,sweep_stop_freq,branches)

    # calculate the difference between the observed and identified harmonics
    simple_hgm_diff = nlsp.cut_spectrum(hgm_harmonics-nlsystem_harmonics,[100,19900])
    lp_hgm_diff = nlsp.cut_spectrum(hgm_lp_harmonics - nlsystem_lp_harmonics,[100,19900])
    up_hgm_diff = nlsp.cut_spectrum(hgm_up_harmonics - nlsystem_up_harmonics,[100,19900])

    # plot the difference
    plot.log()
    print "Simple hammerstein model harmonics plot"
    plot.plot(simple_hgm_diff)
    print "Lowpass hammerstein model harmonics plot"
    plot.plot(lp_hgm_diff)
    print "Upsampling hammerstein model harmonics plot"
    plot.plot(up_hgm_diff)

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
nonlinear_functions_chebyshev = nlsp.nonlinearconvolution_chebyshev_nlfunction(branches)
#nonlinear_functions_power = [nlsp.function_factory.power_series(1),]*branches
#nonlinear_functions_chebyshev = [nlsp.function_factory.chebyshev1_polynomial(1),]*branches

# Filter Specifications
filter_spec_tofind = nlsp.log_bpfilter(sweep_start_freq,sweep_stop_freq,branches,input_sweep)
#filter_spec_tofind = [sumpf.modules.ImpulseGenerator(samplingrate=input_sweep.GetSamplingRate(),length=len(input_sweep)).GetSignal(),]*branches

# Max harmonics
max_harmonics = [1,2,3,4,5]
#max_harmonics = [1,]*branches

harmonics_difference_powerseries_evaluation()
# harmonics_difference_chebyshev_evaluation()