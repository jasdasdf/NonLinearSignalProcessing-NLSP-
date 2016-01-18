import sumpf
import nlsp
import _common as common
import common.plot as plot

def nonlinearfunction_test():
    sweep_samplingrate = 48000
    sweep_length = 2**18
    ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sweep_samplingrate,length=sweep_length)
    hmodel = nlsp.HammersteinModel(input_signal=ip_sweep_signal.GetSignal())
    hmodel.SetNLFunction(nonlin_func=nlsp.function_factory.power_series(5))
    hmodel_1 = nlsp.HammersteinModel(input_signal=ip_sweep_signal.GetSignal(),
                                   nonlin_func=nlsp.function_factory.power_series(5))
    hmodel_1.SetNLFunction(nonlin_func=lambda x:x)
    energy = common.calculateenergy(hmodel.GetOutput())
    energy_1 = common.calculateenergy(hmodel_1.GetOutput())
    print energy,energy_1

nonlinearfunction_test()