import sumpf
import nlsp
import common

sweep_samplingrate = 48000
sweep_length = 2**18
plot = True

def reliabilityofaliasing(sweep_samplingrate, sweep_length):
    """
    Evaluation of the model for linearity.
    The polynomial block power is set to one, so it produces only linear output. But aliasing compensation is done
    to prevent higher order harmonics.
    expectation: the upsampling hammerstein block should not produce any attenuation but the lp hammerstein block should
    produce attenuation due to lowpass filtering operation in the linear block.
    :param sweep_samplingrate: the sampling rate of the input sweep which is given to the model
    :param sweep_lenth:  the length of the input sweep which is given to the model
    :return:
    """
    ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sweep_samplingrate,length=sweep_length)
    ip_sweep_spec = sumpf.modules.FourierTransform(ip_sweep_signal)
    UPHModel = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=ip_sweep_signal.GetSignal(),
                                                             nonlin_func=nlsp.NonlinearFunction.power_series(1))
    LPHModel = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal.GetSignal(),
                                                             nonlin_func=nlsp.NonlinearFunction.power_series(1),
                                                             filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                                             filterorder=100)
    DOWNHModel = nlsp.AliasCompensatingHammersteinModelDownandUp(input_signal=ip_sweep_signal.GetSignal(),
                                                                 nonlin_func=nlsp.NonlinearFunction.power_series(1))
    print LPHModel.GetMaximumHarmonic()
    print UPHModel.GetMaximumHarmonic()
    print DOWNHModel.GetMaximumHarmonic()
    UPHModel.SetMaximumHarmonic(2)
    LPHModel.SetMaximumHarmonic(2)
    DOWNHModel.SetMaximumHarmonic(2)
    print LPHModel.GetMaximumHarmonic()
    print UPHModel.GetMaximumHarmonic()
    print DOWNHModel.GetMaximumHarmonic()

    if plot is True:
        # down sampling model plot - signal
        common.plot.plot(ip_sweep_signal.GetSignal(), show=False)
        common.plot.plot(DOWNHModel.GetNLOutput(), show=False)
        common.plot.plot(DOWNHModel.GetOutput(), show=True)
        # up sampling model plot - signal
        common.plot.plot(ip_sweep_signal.GetSignal(), show=False)
        common.plot.plot(UPHModel.GetNLOutput(), show=False)
        common.plot.plot(UPHModel.GetOutput(), show=True)
        # lowpass model plot - signal
        common.plot.plot(ip_sweep_signal.GetSignal(), show=False)
        common.plot.plot(LPHModel.GetNLOutput(), show=False)
        common.plot.plot(LPHModel.GetOutput(), show=True)

        common.plot.log()
        # down sampling model plot - spectrum
        common.plot.plot(sumpf.modules.FourierTransform(signal=ip_sweep_signal.GetSignal()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=DOWNHModel.GetNLOutput()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=DOWNHModel.GetOutput()).GetSpectrum(), show=True)
        # up sampling model plot - spectrum
        common.plot.plot(sumpf.modules.FourierTransform(signal=ip_sweep_signal.GetSignal()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=UPHModel.GetNLOutput()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=UPHModel.GetOutput()).GetSpectrum(), show=True)
        # lowpass model plot - spectrum
        common.plot.plot(sumpf.modules.FourierTransform(signal=ip_sweep_signal.GetSignal()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=LPHModel.GetNLOutput()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=LPHModel.GetOutput()).GetSpectrum(), show=True)


reliabilityofaliasing(sweep_samplingrate, sweep_length)