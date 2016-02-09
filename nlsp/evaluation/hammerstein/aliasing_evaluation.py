import numpy
import sumpf
import nlsp
import common.plot as plot

def simplevslpvsup_snrandmse_evaluation():
    for i in range(1,degree+1):
        input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length,
                                                   start_frequency=sweep_start_freq,
                                                   stop_frequency=sweep_stop_freq).GetSignal()
        branch_simple = nlsp.HammersteinModel(input_signal=input_sweep,
                                              nonlin_func=nlsp.function_factory.power_series(i))
        branch_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input_sweep,
                                                                    nonlin_func=nlsp.function_factory.power_series(i),
                                                                    max_harm=i)
        branch_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=input_sweep,
                                                                  nonlin_func=nlsp.function_factory.power_series(i),
                                                                  max_harm=i)
        print "Order: %r" %i
        print "SNR of simple h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_sweep, branch_simple.GetOutput(),
                                                                              [50,19900])
        print "SNR of upsample h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_sweep, branch_up.GetOutput(),
                                                                              [50,19900])
        print "SNR of lowpass h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_sweep, branch_lp.GetOutput(),
                                                                              [50,19900])
        print "MSE of simple h. branch: %r" %nlsp.mean_squared_error_time_range(input_sweep, branch_simple.GetOutput(),
                                                                              [50,19900])
        print "MSE of upsample h. branch: %r" %nlsp.mean_squared_error_time_range(input_sweep, branch_up.GetOutput(),
                                                                              [50,19900])
        print "MSE of lowpass h. branch: %r" %nlsp.mean_squared_error_time_range(input_sweep, branch_lp.GetOutput(),
                                                                              [50,19900])
        plot.log()
        plot.plot(sumpf.modules.FourierTransform(branch_simple.GetOutput()).GetSpectrum(),show=False)
        plot.plot(sumpf.modules.FourierTransform(branch_lp.GetOutput()).GetSpectrum(),show=True)
        plot.plot(sumpf.modules.FourierTransform(branch_up.GetOutput()).GetSpectrum(),show=True)

def simplevslpvsup_puretone_evaluation():
    """
    Evaluation of alias compensation of hammerstein branch using pure tones.
    Puretone of certain frequency is given to different hammerstein branches with different Aliasing compensation.
    The order of the harmonics produces is changed and the output of different models are plotted.
    We observe the lowpass aliasing compensation completely filters out the signal harmonics even when they are in the
    baseband freq.
    """
    for i in range(1,degree+1):
        input_tone = sumpf.modules.SineWaveGenerator(frequency=puretone_freq,
                                                     phase=0.0,
                                                     samplingrate=sampling_rate,
                                                     length=length).GetSignal()
        branch_simple = nlsp.HammersteinModel(input_signal=input_tone,
                                              nonlin_func=nlsp.function_factory.power_series(i))
        branch_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input_tone,
                                                                    nonlin_func=nlsp.function_factory.power_series(i),
                                                                    max_harm=i)
        branch_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=input_tone,
                                                                  nonlin_func=nlsp.function_factory.power_series(i),
                                                                  max_harm=i)
        print "Order: %r" %i
        print "SNR of simple h. branch: %r" %nlsp.signal_to_noise_ratio_freq_range(input_tone, branch_simple.GetOutput(),
                                                                              [sweep_start_freq,sweep_stop_freq])
        print "SNR of upsample h. branch: %r" %nlsp.signal_to_noise_ratio_freq_range(input_tone, branch_up.GetOutput(),
                                                                              [sweep_start_freq,sweep_stop_freq])
        print "SNR of lowpass h. branch: %r" %nlsp.signal_to_noise_ratio_freq_range(input_tone, branch_lp.GetOutput(),
                                                                              [sweep_start_freq,sweep_stop_freq])
        print "MSE of simple h. branch: %r" %nlsp.mean_squared_error_freq_range(input_tone, branch_simple.GetOutput(),
                                                                              [sweep_start_freq,sweep_stop_freq])
        print "MSE of upsample h. branch: %r" %nlsp.mean_squared_error_freq_range(input_tone, branch_up.GetOutput(),
                                                                              [sweep_start_freq,sweep_stop_freq])
        print "MSE of lowpass h. branch: %r" %nlsp.mean_squared_error_freq_range(input_tone, branch_lp.GetOutput(),
                                                                              [sweep_start_freq,sweep_stop_freq])
        plot.log()
        branch_simple_spectrum = nlsp.relabel(sumpf.modules.FourierTransform(branch_simple.GetOutput()).GetSpectrum(),
                                              "%d Simple Hammerstein Branch"%i)
        plot.plot(branch_simple_spectrum,show=False)
        branch_up_spectrum = nlsp.relabel(sumpf.modules.FourierTransform(branch_up.GetOutput()).GetSpectrum(),
                                              "%d Upsampling Hammerstein Branch"%i)
        plot.plot(branch_up_spectrum,show=False)
        branch_lp_spectrum = nlsp.relabel(sumpf.modules.FourierTransform(branch_lp.GetOutput()).GetSpectrum(),
                                              "%d Lowpass Hammerstein Branch"%i)
        plot.plot(branch_lp_spectrum,show=True)

def simplevslpvsup_sweep_evaluation():
    """
    Evaluation of alias compensation of hammerstein branch using sweep.
    Sweep(20 to 20000Hz) of sampling rate 48000 samples/sec is upsampled to 96000 samples/sec and given to upsampling
    and lowpass filtering Alias compensation. And the maximum harmonic of the hammerstein branches is changed to two
    and the energy of the branches is evaluated.
    The energy of the desired band and undesired band should be equal for both upsampling and lowpass filtering alias
    compensation.
    """
    ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length,start_frequency=sweep_start_freq,
                                                   stop_frequency=sweep_stop_freq).GetSignal()
    up_sweep_signal = sumpf.modules.ResampleSignal(signal=ip_sweep_signal,
                                                   samplingrate=ip_sweep_signal.GetSamplingRate()*2).GetOutput()
    branch = nlsp.HammersteinModel(input_signal=up_sweep_signal,
                                   nonlin_func=nlsp.function_factory.power_series(1))
    branch_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=up_sweep_signal,
                                                             nonlin_func=nlsp.function_factory.power_series(1),
                                                             max_harm=1)
    branch_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=up_sweep_signal,
                                                             nonlin_func=nlsp.function_factory.power_series(1),
                                                             max_harm=1,
                                                             filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100))
    energy_full_lp = nlsp.calculateenergy_freq(branch_lp.GetOutput())
    energy_full_up = nlsp.calculateenergy_freq(branch_up.GetOutput())
    energy_full = nlsp.calculateenergy_freq(branch.GetOutput())
    energy_limit_lp = nlsp.calculateenergy_betweenfreq_freq(branch_lp.GetOutput(),[sweep_stop_freq,sampling_rate])
    energy_limit_up = nlsp.calculateenergy_betweenfreq_freq(branch_up.GetOutput(),[sweep_stop_freq,sampling_rate])
    energy_limit = nlsp.calculateenergy_betweenfreq_freq(branch.GetOutput(),[sweep_stop_freq,sampling_rate])
    print "Energy before compensation, full, lp:%r, up:%r, simple:%r" %(energy_full_lp,energy_full_up,energy_full)
    print "Energy before compensation, limit, lp:%r, up:%r, simple:%r" %(energy_limit_lp,energy_limit_up,energy_limit)
    branch_up.SetMaximumHarmonic(2)
    branch_lp.SetMaximumHarmonic(2)
    energy_full_lp = nlsp.calculateenergy_freq(branch_lp.GetOutput())
    energy_full_up = nlsp.calculateenergy_freq(branch_up.GetOutput())
    energy_limit_lp = nlsp.calculateenergy_betweenfreq_freq(branch_lp.GetOutput(),[sweep_stop_freq,sampling_rate])
    energy_limit_up = nlsp.calculateenergy_betweenfreq_freq(branch_up.GetOutput(),[sweep_stop_freq,sampling_rate])
    print "Energy after compensation, full, lp:%r, up:%r" %(energy_full_lp,energy_full_up)
    print "Energy after compensation, limit, lp:%r, up:%r" %(energy_limit_lp,energy_limit_up)
    plot.log()
    lp_spec = sumpf.modules.FourierTransform(branch_lp.GetOutput()).GetSpectrum()
    up_spec = sumpf.modules.FourierTransform(branch_lp.GetOutput()).GetSpectrum()
    plot.plot(nlsp.relabel(lp_spec,"Lowpass Alias compensation spectrum"),show=False)
    plot.plot(nlsp.relabel(up_spec,"Upsampling Alias compensation spectrum"),show=True)

def lowpass_evaluation():
    for order in range(1,degree+1):
        ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length,start_frequency=sweep_start_freq,
                                                       stop_frequency=sweep_stop_freq).GetSignal()
        branch_lp_butter = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal,
                                                                 nonlin_func=nlsp.function_factory.power_series(1),
                                                                 max_harm=order,
                                                                 filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=10))
        branch_lp_cheby1 = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal,
                                                                 nonlin_func=nlsp.function_factory.power_series(1),
                                                                 max_harm=order,
                                                                 filterfunction=sumpf.modules.FilterGenerator.CHEBYCHEV1(order=10,ripple=6.0))
        branch_lp_bessel = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal,
                                                                 nonlin_func=nlsp.function_factory.power_series(1),
                                                                 max_harm=order,
                                                                 filterfunction=sumpf.modules.FilterGenerator.BESSEL(order=30))
        butter_spec = nlsp.relabel(sumpf.modules.FourierTransform(branch_lp_butter.GetOutput()).GetSpectrum(),
                                   "butterworth lp branch")
        chebyshev_spec = nlsp.relabel(sumpf.modules.FourierTransform(branch_lp_cheby1.GetOutput()).GetSpectrum(),
                                   "chebyshev lp branch")
        input_spec = nlsp.relabel(sumpf.modules.FourierTransform(ip_sweep_signal).GetSpectrum(),
                                   "input spec")
        plot.log()
        plot.plot(butter_spec,show=False)
        plot.plot(input_spec,show=False)
        plot.plot(chebyshev_spec,show=True)

def harmonics_evaluation():
    for i in range(1,degree+1):
        ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length,start_frequency=sweep_start_freq,
                                                       stop_frequency=sweep_stop_freq).GetSignal()
        branch_simple = nlsp.HammersteinModel(input_signal=ip_sweep_signal,
                                              nonlin_func=nlsp.function_factory.power_series(i))
        branch_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=ip_sweep_signal,
                                                                    nonlin_func=nlsp.function_factory.power_series(i),
                                                                    max_harm=i)
        branch_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal,
                                                                  nonlin_func=nlsp.function_factory.power_series(i),
                                                                  max_harm=i)
        # plot.log()
        # plot.plot(ip_harmonics,show=False)
        # plot.plot(ip_harmonics_up,show=False)
        # plot.plot(ip_harmonics_lp,show=True)
        print nlsp.harmonicsvsall_energyratio(branch_simple.GetOutput(),ip_sweep_signal,i,sweep_start_freq,sweep_stop_freq,degree)
        print nlsp.harmonicsvsall_energyratio(branch_lp.GetOutput(),ip_sweep_signal,i,sweep_start_freq,sweep_stop_freq,degree)
        print nlsp.harmonicsvsall_energyratio(branch_up.GetOutput(),ip_sweep_signal,i,sweep_start_freq,sweep_stop_freq,degree)
        print
        print


sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
degree = 5
puretone_freq = 10000
length = 2**20

# simplevslpvsup_snrandmse_evaluation()
# simplevslpvsup_puretone_evaluation()
# simplevslpvsup_sweep_evaluation()
# lowpass_evaluation()
harmonics_evaluation()