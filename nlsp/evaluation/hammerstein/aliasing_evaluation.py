import numpy
import sumpf
import nlsp
import nlsp.common.plots as plot


def puretone_evaluation():
    """
    Evaluation of alias compensation of hammerstein branch using pure tones.
    Puretone of certain frequency is given to different hammerstein branches with different Aliasing compensation.
    The order of the harmonics produces is changed and the output of different models are plotted.
    We observe the lowpass aliasing compensation completely filters out the signal harmonics even when they are in the
    baseband freq.
    """
    print "puretone evaluation"
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
        print "Pure tone evaluation"
        print "Order: %r" %i
        print "SNR of simple h. branch: %r" %nlsp.snr(input_tone, branch_simple.GetOutput())
        print "SNR of upsample h. branch: %r" %nlsp.snr(input_tone, branch_up.GetOutput())
        print "SNR of lowpass h. branch: %r" %nlsp.snr(input_tone, branch_lp.GetOutput())
        print "MSE of simple h. branch: %r" %nlsp.mean_squared_error_time(input_tone, branch_simple.GetOutput())
        print "MSE of upsample h. branch: %r" %nlsp.mean_squared_error_time(input_tone, branch_up.GetOutput())
        print "MSE of lowpass h. branch: %r" %nlsp.mean_squared_error_time(input_tone, branch_lp.GetOutput())
        if Plot is True:
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

def sweep_evaluation():
    """
    Evaluation of alias compensation of hammerstein branch using sweep.
    Sweep(20 to 20000Hz) of sampling rate 48000 samples/sec is upsampled to 96000 samples/sec and given to upsampling
    and lowpass filtering Alias compensation. And the maximum harmonic of the hammerstein branches is changed to two
    and the energy of the branches is evaluated.
    The energy of the desired band and undesired band should be equal for both upsampling and lowpass filtering alias
    compensation.
    """
    print "sweep evaluation"
    up_sweep_signal = sumpf.modules.ResampleSignal(signal=input_sweep_signal,
                                                   samplingrate=input_sweep_signal.GetSamplingRate()*2).GetOutput()
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
    if Plot is True:
        plot.log()
        lp_spec = sumpf.modules.FourierTransform(branch_lp.GetOutput()).GetSpectrum()
        up_spec = sumpf.modules.FourierTransform(branch_lp.GetOutput()).GetSpectrum()
        plot.plot(nlsp.relabel(lp_spec,"Lowpass Alias compensation spectrum"),show=False)
        plot.plot(nlsp.relabel(up_spec,"Upsampling Alias compensation spectrum"),show=True)

def lowpass_evaluation():
    print "lowpass evaluation"
    for order in range(1,degree+1):
        branch_lp_butter = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=input_sweep_signal,
                                                                 nonlin_func=nlsp.function_factory.power_series(1),
                                                                 max_harm=order,
                                                                 filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=10))
        branch_lp_cheby1 = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=input_sweep_signal,
                                                                 nonlin_func=nlsp.function_factory.power_series(1),
                                                                 max_harm=order,
                                                                 filterfunction=sumpf.modules.FilterGenerator.CHEBYCHEV1(order=10,ripple=6.0))
        butter_spec = nlsp.relabel(sumpf.modules.FourierTransform(branch_lp_butter.GetOutput()).GetSpectrum(),
                                   "butterworth lp branch")
        chebyshev_spec = nlsp.relabel(sumpf.modules.FourierTransform(branch_lp_cheby1.GetOutput()).GetSpectrum(),
                                   "chebyshev lp branch")
        input_spec = nlsp.relabel(sumpf.modules.FourierTransform(input_sweep_signal).GetSpectrum(),
                                   "input spec")
        if Plot is True:
            plot.log()
            plot.plot(butter_spec,show=False)
            plot.plot(input_spec,show=False)
            plot.plot(chebyshev_spec,show=True)

def harmonics_evaluation():
    print "harmonics evaluation"
    for i in range(3,degree+1):
        branch_simple = nlsp.HammersteinModel(input_signal=input_sweep_signal,
                                              nonlin_func=nlsp.function_factory.power_series(i))
        branch_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input_sweep_signal,
                                                                    nonlin_func=nlsp.function_factory.power_series(i),
                                                                    max_harm=i)
        branch_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=input_sweep_signal,
                                                                  nonlin_func=nlsp.function_factory.power_series(i),
                                                                  max_harm=i)
        harm_simple = nlsp.get_sweep_harmonics_ir(input_sweep_signal,branch_simple.GetOutput(),sweep_start_freq,
                                                        sweep_stop_freq,length,degree)
        harm_lp = nlsp.get_sweep_harmonics_ir(input_sweep_signal,branch_lp.GetOutput(),sweep_start_freq,
                                                        sweep_stop_freq,length,degree)
        harm_up = nlsp.get_sweep_harmonics_ir(input_sweep_signal,branch_up.GetOutput(),sweep_start_freq,
                                                        sweep_stop_freq,length,degree)
        print "degree %r" %i
        print nlsp.calculateenergy_freq(harm_simple)
        print nlsp.calculateenergy_freq(harm_lp)
        print nlsp.calculateenergy_freq(harm_up)
        print
        print
        print nlsp.harmonicsvsall_energyratio(branch_simple.GetOutput(),input_sweep_signal,i,sweep_start_freq,
                                              sweep_stop_freq,length,degree)
        print nlsp.harmonicsvsall_energyratio(branch_lp.GetOutput(),input_sweep_signal,i,sweep_start_freq,
                                              sweep_stop_freq,length,degree)
        print nlsp.harmonicsvsall_energyratio(branch_up.GetOutput(),input_sweep_signal,i,sweep_start_freq,
                                              sweep_stop_freq,length,degree)
        print
        print
        if Plot is True:
            plot.plot(harm_simple)
            plot.plot(harm_up)
            plot.plot(harm_lp)

def higher_nonlinearity_evaluation():
    print "higher nonlinearity evaluation"
    model_up_ref = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input_sweep_signal,
                                                               nonlin_func=nlsp.function_factory.power_series(degree),
                                                               max_harm=degree)
    model_lp_ref = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=input_sweep_signal,
                                                                 nonlin_func=nlsp.function_factory.power_series(degree),
                                                                 max_harm=degree)
    model_up_ref = model_up_ref.GetOutput()
    model_lp_ref = model_lp_ref.GetOutput()
    for factor in range(1,degree+1):
        model_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=input_sweep_signal,
                                                                    nonlin_func=nlsp.function_factory.power_series(degree),
                                                                    max_harm=factor)
        model_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=input_sweep_signal,
                                                                  nonlin_func=nlsp.function_factory.power_series(degree),
                                                                  max_harm=factor)
        model_up = model_up.GetOutput()
        model_lp = model_lp.GetOutput()
        print "Upsampling HM, nonlinearity degree:%r, Alias compensation factor:%r, SNR:%r" %(degree,factor,nlsp.snr(model_up,model_up_ref))
        print "Lowpass HM, nonlinearity degree:%r, Alias compensation factor:%r, SNR:%r" %(degree,factor,nlsp.snr(model_lp,model_lp_ref))
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(model_up).GetSpectrum(),"Upsampling HM",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(model_up_ref).GetSpectrum(),"Upsampling HM Ref")
            plot.relabelandplot(sumpf.modules.FourierTransform(model_lp).GetSpectrum(),"Lowpass HM",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(model_lp_ref).GetSpectrum(),"Lowpass HM Ref")

def wgn_evaluation():
    degree = 5
    print "wgn evaluation"
    for degree in range(3,degree+1):
        wgn = sumpf.modules.NoiseGenerator(sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0),
                                           samplingrate=sampling_rate,
                                           length=length)
        prp = sumpf.modules.ChannelDataProperties()
        prp.SetSignal(wgn.GetSignal())
        filter = sumpf.modules.RectangleFilterGenerator(resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
        ref = nlsp.HammersteinModel(input_signal=wgn.GetSignal(),nonlin_func=nlsp.function_factory.power_series(degree),
                                      filter_impulseresponse=sumpf.modules.InverseFourierTransform(filter).GetSignal()).GetOutput()
        model_simple = nlsp.HammersteinModel(input_signal=wgn.GetSignal(),
                                              nonlin_func=nlsp.function_factory.power_series(degree))
        model_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=wgn.GetSignal(),
                                                                    nonlin_func=nlsp.function_factory.power_series(degree),
                                                                    max_harm=degree)
        model_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=wgn.GetSignal(),
                                                                  nonlin_func=nlsp.function_factory.power_series(degree),
                                                                  max_harm=degree)
        print "degree %r" %degree
        print nlsp.snr(model_simple.GetOutput(),ref)
        print nlsp.snr(model_up.GetOutput(),ref)
        print nlsp.snr(model_lp.GetOutput(),ref)
        print
        print
        if Plot is True:
            plot.relabelandplot(sumpf.modules.FourierTransform(model_up.GetOutput()).GetSpectrum(),"Upsampling HM",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(ref).GetSpectrum(),"Upsampling HM Ref")
            plot.relabelandplot(sumpf.modules.FourierTransform(model_lp.GetOutput()).GetSpectrum(),"Lowpass HM",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(ref).GetSpectrum(),"Lowpass HM Ref")

def linearity_evaluation():
    print "linearity evaluation"
    for i in range(3,degree+1):
        max_harm = i
        nl_degree = i
        sweep_start_freq = 20.0
        sweep_stop_freq = 4000.0
        ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length,start_frequency=sweep_start_freq,
                                                       stop_frequency=sweep_stop_freq).GetSignal()
        model_simple = nlsp.HammersteinModel(input_signal=ip_sweep_signal,
                                              nonlin_func=nlsp.function_factory.power_series(nl_degree))
        model_up = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=ip_sweep_signal,
                                                                    nonlin_func=nlsp.function_factory.power_series(nl_degree),
                                                                    max_harm=max_harm)
        model_lp = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal,
                                                                  nonlin_func=nlsp.function_factory.power_series(nl_degree),
                                                                  max_harm=max_harm)
        simple_ref = model_simple.GetOutput()
        up_ip = model_up.GetOutput()
        lp_ip = model_lp.GetOutput()
        print "degree %r" %i
        print nlsp.snr(simple_ref,simple_ref)
        print nlsp.snr(up_ip,simple_ref)
        print nlsp.snr(lp_ip,simple_ref)
        print
        print
        if Plot is True:
            plot.log()
            plot.relabelandplot(sumpf.modules.FourierTransform(model_simple.GetOutput()).GetSpectrum(),"Reference",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(model_up.GetOutput()).GetSpectrum(),"Upsampling HM",show=False)
            plot.relabelandplot(sumpf.modules.FourierTransform(model_lp.GetOutput()).GetSpectrum(),"Lowpass HM",show=True)

sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
degree = 5
puretone_freq = 10000
length = 2**18
Plot = False
silence_duration = 0.02
fade_out = 0.02
fade_in = 0.02

input_signal = nlsp.WindowedSweepGenerator(sampling_rate=sampling_rate, length=length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, silence_duration= silence_duration,fade_out= fade_out,
                                           fade_in=fade_in)
sweep_start_freq,sweep_stop_freq,length = input_signal.GetProperties()
input_sweep_signal = input_signal.GetOutput()

# lowpass_evaluation()
puretone_evaluation()
sweep_evaluation()
harmonics_evaluation()
higher_nonlinearity_evaluation()
wgn_evaluation()
linearity_evaluation()