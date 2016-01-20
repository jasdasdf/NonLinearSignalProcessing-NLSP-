import sumpf
import nlsp
import common.plot as plot

def hgm_evaluation():

    samplingrate = 48000.0
    length = 2**16
    sweep = sumpf.modules.SweepGenerator(samplingrate=samplingrate, length=length).GetSignal()
    imp = sumpf.modules.ImpulseGenerator(samplingrate=samplingrate, length=length).GetSignal()
    hgm = nlsp.HammersteinGroupModel(nonlinear_functions=(nlsp.function_factory.power_series(1),
                                                                     nlsp.function_factory.power_series(1),
                                                                     nlsp.function_factory.power_series(1),
                                                                     nlsp.function_factory.power_series(1)),
                                     filter_irs=(imp,imp,imp,imp), max_harmonics=(1,2,3,4))
    hgm.SetInput(sweep)
    plot.plot(hgm.GetOutput())
    hgm.SetNLFunctions((nlsp.function_factory.power_series(1),nlsp.function_factory.power_series(2),
                        nlsp.function_factory.power_series(3),nlsp.function_factory.power_series(4)))
    # hgm.SetMaximumHarmonics((1,2,3,4))
    plot.plot(hgm.GetHammersteinBranchOutput(1))

hgm_evaluation()
