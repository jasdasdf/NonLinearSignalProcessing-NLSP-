import numpy
import sumpf
import nlsp
import common.plot as plot

def snr_mse_sweep_evaluation():
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

def snr_mse_puretone_evaluation():
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
        print "SNR of simple h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_tone, branch_simple.GetOutput(),
                                                                              [50,19900])
        print "SNR of upsample h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_tone, branch_up.GetOutput(),
                                                                              [50,19900])
        print "SNR of lowpass h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_tone, branch_lp.GetOutput(),
                                                                              [50,19900])
        print "MSE of simple h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_tone, branch_simple.GetOutput(),
                                                                              [50,19900])
        print "MSE of upsample h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_tone, branch_up.GetOutput(),
                                                                              [50,19900])
        print "MSE of lowpass h. branch: %r" %nlsp.signal_to_noise_ratio_time_range(input_tone, branch_lp.GetOutput(),
                                                                              [50,19900])
        plot.log()
        plot.plot(sumpf.modules.FourierTransform(branch_simple.GetOutput()).GetSpectrum(),show=False)
        plot.plot(sumpf.modules.FourierTransform(branch_lp.GetOutput()).GetSpectrum(),show=True)
        plot.plot(sumpf.modules.FourierTransform(branch_up.GetOutput()).GetSpectrum(),show=True)

def lpvsup_evaluation():
    ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length,start_frequency=sweep_start_freq,
                                                   stop_frequency=sweep_stop_freq).GetSignal()
    ip_sweep_signal = sumpf.modules.ResampleSignal(signal=ip_sweep_signal,
                                                   samplingrate=ip_sweep_signal.GetSamplingRate()*2).GetOutput()
    # filter_ir = sumpf.modules.ImpulseGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    # filter_ir = sumpf.modules.ResampleSignal(signal=filter_ir,
    #                                                samplingrate=filter_ir.GetSamplingRate()*2).GetOutput()
    branch_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=ip_sweep_signal,
                                                             nonlin_func=nlsp.function_factory.power_series(1),
                                                             max_harm=1)
    branch_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal,
                                                             nonlin_func=nlsp.function_factory.power_series(1),
                                                             max_harm=1,
                                                             filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100))
    energy_full_lp = nlsp.calculateenergy_time(branch_lp.GetOutput())
    energy_full_up = nlsp.calculateenergy_time(branch_up.GetOutput())
    energy_limit_lp = nlsp.calculateenergy_betweenfreq_freq(branch_lp.GetOutput(),[sampling_rate/2,sampling_rate])
    energy_limit_up = nlsp.calculateenergy_betweenfreq_freq(branch_up.GetOutput(),[sampling_rate/2,sampling_rate])
    print (energy_full_lp,energy_full_up)
    print (energy_limit_lp,energy_limit_up)
    branch_up.SetMaximumHarmonic(5)
    branch_lp.SetMaximumHarmonic(5)
    energy_full_lp = nlsp.calculateenergy_time(branch_lp.GetOutput())
    energy_full_up = nlsp.calculateenergy_time(branch_up.GetOutput())
    energy_limit_lp = nlsp.calculateenergy_betweenfreq_freq(branch_lp.GetOutput(),[sampling_rate/2,sampling_rate])
    energy_limit_up = nlsp.calculateenergy_betweenfreq_freq(branch_up.GetOutput(),[sampling_rate/2,sampling_rate])
    print (energy_full_lp,energy_full_up)
    print (energy_limit_lp,energy_limit_up)
    plot.log()
    # plot.plot(sumpf.modules.FourierTransform(ip_sweep_signal).GetSpectrum(),show=False)
    # plot.plot(sumpf.modules.FourierTransform(branch_lp.GetOutput()).GetSpectrum(),show=False)
    # plot.plot(sumpf.modules.FourierTransform(branch_up.GetOutput()).GetSpectrum(),show=True)


sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 23000.0
degree = 5
puretone_freq = 15000
length = 2**15

# snr_mse_sweep_evaluation()
# snr_mse_puretone_evaluation()
lpvsup_evaluation()