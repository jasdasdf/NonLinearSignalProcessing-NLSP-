import sumpf
import nlsp
import common

sweep_samplingrate = 48000
sweep_length = 2**16
plot = False

def resampler_evaluation():
    """
    Evaluation of the Resampler with sweep and impulse response. Both impulse and sweep are upsampled or downsampled
    and then their transfer function is multiplied to get the output.
    we expect that the amp of the output is either increased or reduced to the upsampling rate or downsampling rate
    times
    """
    upsampling_rate = 3
    downsampling_rate = 2
    ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sweep_samplingrate, length=sweep_length).GetSignal()
    ip_impulse = sumpf.modules.ImpulseGenerator(samplingrate=sweep_samplingrate,length=sweep_length).GetSignal()
    upsweep = sumpf.modules.ResampleSignal(signal=ip_sweep_signal,
                                           samplingrate=sweep_samplingrate*upsampling_rate).GetOutput()
    upimp = sumpf.modules.ResampleSignal(signal=ip_impulse,
                                         samplingrate=sweep_samplingrate*upsampling_rate).GetOutput()
    m1 = sumpf.modules.MultiplySpectrums(spectrum1=sumpf.modules.FourierTransform(upsweep).GetSpectrum(),
                                        spectrum2=sumpf.modules.FourierTransform(upimp).GetSpectrum()).GetOutput()
    downsweep = sumpf.modules.ResampleSignal(signal=ip_sweep_signal,
                                           samplingrate=sweep_samplingrate/downsampling_rate).GetOutput()
    downimp = sumpf.modules.ResampleSignal(signal=ip_impulse,
                                         samplingrate=sweep_samplingrate/downsampling_rate).GetOutput()
    m2 = sumpf.modules.MultiplySpectrums(spectrum1=sumpf.modules.FourierTransform(downsweep).GetSpectrum(),
                                        spectrum2=sumpf.modules.FourierTransform(downimp).GetSpectrum()).GetOutput()
    common.plot.plot(sumpf.modules.InverseFourierTransform(m1).GetSignal(),show=False)
    common.plot.plot(upsweep)
    common.plot.plot(sumpf.modules.InverseFourierTransform(m2).GetSignal(),show=False)
    common.plot.plot(downsweep)


def resampler_compensation_evaluation():
    """
    Evaluation of the Upsampling and Downsampling alias compensating hammerstein model.
    The nonlinear block of hammerstein model is set to the power series of 1 but the maximum harmonics is set to higher
    value and evaluate for the attenuation introduced by alias compensation.
    we expect the input and the output is of same amplitude. and the low pass alias compensation introduces attenuation
    by lowpass filtering whereas the upsampling alias compensation model should be ideal
    """
    max_harm = 2
    ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sweep_samplingrate, length=sweep_length).GetSignal()
    ip_impulse = sumpf.modules.ImpulseGenerator(samplingrate=sweep_samplingrate,length=sweep_length).GetSignal()
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(ip_sweep_signal)
    filter = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                           frequency=24000,resolution=prp.GetResolution(),
                                           length=prp.GetSpectrumLength()).GetSpectrum()
    filterip = sumpf.modules.InverseFourierTransform(spectrum=filter).GetSignal()
    UPHModel_imp = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=ip_sweep_signal,
                                                               nonlin_func=nlsp.function_factory.power_series(1),
                                                               max_harm=max_harm,
                                                               filter_impulseresponse=ip_impulse)
    UPHModel_filt = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=ip_sweep_signal,
                                                               nonlin_func=nlsp.function_factory.power_series(1),
                                                               max_harm=max_harm,
                                                               filter_impulseresponse=filterip)
    DownHModel_imp = nlsp.AliasCompensatingHammersteinModelDownandUp(input_signal=ip_sweep_signal,
                                                               nonlin_func=nlsp.function_factory.power_series(1),
                                                               max_harm=max_harm,
                                                               filter_impulseresponse=ip_impulse)
    DownHModel_filt = nlsp.AliasCompensatingHammersteinModelDownandUp(input_signal=ip_sweep_signal,
                                                               nonlin_func=nlsp.function_factory.power_series(1),
                                                               max_harm=max_harm,
                                                               filter_impulseresponse=filterip)
    common.plot.plot(ip_sweep_signal,show=False)
    common.plot.plot(UPHModel_imp.GetOutput(),show=False)
    common.plot.plot(UPHModel_filt.GetOutput(),show=True)
    common.plot.plot(ip_sweep_signal,show=False)
    common.plot.plot(DownHModel_imp.GetOutput(),show=False)
    common.plot.plot(DownHModel_filt.GetOutput(),show=True)

resampler_compensation_evaluation()
resampler_evaluation()
