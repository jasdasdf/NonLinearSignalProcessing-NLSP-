import sumpf
import nlsp
import _common as common

def test_nonlinearfunction():
    """
    test whether the factory function and the function for nonlinearity generation works fine.
    the nonlinear function is called in three different methods with same input signal and same degree of
    nonlinearity. Hence the output of the model should have same output.
    The comparision is made by comaparing the energy of the output signals
    """
    sweep_samplingrate = 48000
    sweep_length = 2**18
    ip_sweep_signal = sumpf.modules.SweepGenerator(samplingrate=sweep_samplingrate,length=sweep_length)
    hmodel = nlsp.HammersteinModel(input_signal=ip_sweep_signal.GetSignal())
    hmodel.SetNLFunction(nonlin_func=nlsp.function_factory.power_series(5))
    hmodel_1 = nlsp.HammersteinModel(input_signal=ip_sweep_signal.GetSignal(),
                                   nonlin_func=nlsp.function_factory.power_series(5))
    energy = common.calculateenergy(hmodel.GetOutput())
    energy_1 = common.calculateenergy(hmodel_1.GetOutput())
    hmodel_2 = nlsp.NonlinearFunction.power_series(5,signal=ip_sweep_signal.GetSignal())
    energy_2 = common.calculateenergy(hmodel_2.GetOutput())
    energy = map(int,energy)
    energy_1 = map(int,energy_1)
    energy_2 = map(int,energy_2)
    assert energy == energy_1 == energy_2
