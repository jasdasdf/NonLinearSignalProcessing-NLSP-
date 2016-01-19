import sumpf
import nlsp
import common

sweep_samplingrate = 4
sweep_length = 4
plot = False


def resampling_evaluation():
    # ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sweep_samplingrate, length=sweep_length)
    ip_sweep_signal = sumpf.modules.ImpulseGenerator(samplingrate=sweep_samplingrate,length=sweep_length)
    ip_sweep_spec = sumpf.modules.FourierTransform(ip_sweep_signal)
    # UPHModel = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=ip_sweep_signal.GetSignal(),
    #                                                            nonlin_func=nlsp.function_factory.power_series(1),
    #                                                            max_harm=2)
    # DOWNHModel = nlsp.AliasCompensatingHammersteinModelDownandUp(input_signal=ip_sweep_signal.GetSignal(),
    #                                                              nonlin_func=nlsp.function_factory.power_series(1),
    #                                                              max_harm=2)
    up = sumpf.modules.ResampleSignal(signal=ip_sweep_signal.GetSignal(),samplingrate=sweep_samplingrate*2).GetOutput()
    down = sumpf.modules.ResampleSignal(signal=ip_sweep_signal.GetSignal(),samplingrate=sweep_samplingrate/2).GetOutput()
    # print ip_sweep_signal.GetSignal().GetChannels()
    # print sumpf.modules.FourierTransform(ip_sweep_signal.GetSignal()).GetSpectrum().GetChannels()
    # print up.GetChannels()
    # print sumpf.modules.FourierTransform(up).GetSpectrum().GetChannels()
    # print down.GetChannels()
    # print sumpf.modules.FourierTransform(down).GetSpectrum().GetChannels()
    # common.plot.plot(ip_sweep_signal.GetSignal(),show=True)
    # common.plot.plot(up,show=True)
    # common.plot.plot(down,show=True)
    # common.plot.log()
    # common.plot.plot(sumpf.modules.FourierTransform(ip_sweep_signal.GetSignal()).GetSpectrum())
    # common.plot.plot(sumpf.modules.FourierTransform(down).GetSpectrum())
    # common.plot.plot(sumpf.modules.FourierTransform(up).GetSpectrum())
    if plot is True:
        # down sampling model plot - signal
        # common.plot.plot(DOWNHModel._itransform.GetSignal(), show=True)
        common.plot.plot(UPHModel.GetNLOutput(),show=False)
        common.plot.plot(UPHModel.GetOutput(), show=True)
        common.plot.plot(DOWNHModel.GetNLOutput(),show=False)
        common.plot.plot(DOWNHModel.GetOutput(), show=True)
        # common.plot.plot(DOWNHModel.GetOutput(), show=True)
        # up sampling model plot - signal
        # common.plot.plot(ip_sweep_signal.GetSignal(), show=False)
        # common.plot.plot(UPHModel.GetNLOutput(), show=False)
        # common.plot.plot(UPHModel.GetOutput(), show=True)

        common.plot.log()
        # down sampling model plot - spectrum
        # common.plot.plot(DOWNHModel._multiply.GetOutput(), show=True)
        # common.plot.plot(sumpf.modules.FourierTransform(signal=DOWNHModel._ampfilter.GetOutput()).GetSpectrum(),
        #                                                 show=False)
        # common.plot.plot(sumpf.modules.FourierTransform(signal=DOWNHModel._downfilter.GetOutput()).GetSpectrum(),
        #                                                 show=True)
        # # common.plot.plot(sumpf.modules.FourierTransform(signal=DOWNHModel.GetOutput()).GetSpectrum(), show=True)
        # up sampling model plot - spectrum
        # common.plot.plot(sumpf.modules.FourierTransform(signal=ip_sweep_signal.GetSignal()).GetSpectrum(), show=False)
        # common.plot.plot(sumpf.modules.FourierTransform(signal=UPHModel.GetNLOutput()).GetSpectrum(), show=False)
        # common.plot.plot(sumpf.modules.FourierTransform(signal=UPHModel.GetOutput()).GetSpectrum(), show=True)


resampling_evaluation()
