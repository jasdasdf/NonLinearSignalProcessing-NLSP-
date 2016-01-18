import sumpf
import nlsp
import common

sweep_samplingrate = 48000
sweep_length = 2**18
plot = True

def linearity_evaluation_upsamplingvslpass(sweep_samplingrate, sweep_length):
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
    UPHModel.SetMaximumHarmonic(2)
    print UPHModel.GetMaximumHarmonic()
    LPHModel = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=ip_sweep_signal.GetSignal(),
                                                             nonlin_func=nlsp.NonlinearFunction.power_series(1),
                                                             filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                                             filterorder=100)
    LPHModel.SetMaximumHarmonic(5)
    print LPHModel.GetMaximumHarmonic()

    if plot is True:
        common.plot.plot(ip_sweep_signal.GetSignal(), show=False)
        common.plot.plot(UPHModel.GetNLOutput(), show=False)
        common.plot.plot(UPHModel.GetOutput(), show=True)
        common.plot.plot(ip_sweep_signal.GetSignal(), show=False)
        common.plot.plot(LPHModel.GetNLOutput(), show=False)
        common.plot.plot(LPHModel.GetOutput(), show=True)
        common.plot.log()
        common.plot.plot(sumpf.modules.FourierTransform(signal=ip_sweep_signal.GetSignal()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=LPHModel.GetNLOutput()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=LPHModel.GetOutput()).GetSpectrum(), show=True)
        common.plot.plot(sumpf.modules.FourierTransform(signal=ip_sweep_signal.GetSignal()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=UPHModel.GetNLOutput()).GetSpectrum(), show=False)
        common.plot.plot(sumpf.modules.FourierTransform(signal=UPHModel.GetOutput()).GetSpectrum(), show=True)


linearity_evaluation_upsamplingvslpass(sweep_samplingrate, sweep_length)