import sumpf
import nlsp
import common

def TestHammersteinModel():
    frequency = 100.0
    samplingrate = 48000.0
    length = samplingrate
    gen = sumpf.modules.SineWaveGenerator(frequency=frequency,
                                          phase=0.0,
                                          samplingrate=samplingrate,
                                          length=length)
    model_sig = nlsp.HammersteinModel(input_signal=gen.GetSignal(),nonlin_func=nlsp.NonlinearFunction.power_series(1))
    model_spec = sumpf.modules.FourierTransform(signal=model_sig.GetOutput())
    common.plot.plot(model_sig.GetOutput())
    common.plot.log()
    common.plot.plot(model_spec.GetSpectrum())

def TestAliasCompensatingHammersteinModelLowpass():
    pass
def TestAliasCompensatingHammersteinModelUpandDown():
    pass
def AliasCompensatingHammersteinModelDownandUp():
    pass

TestHammersteinModel()