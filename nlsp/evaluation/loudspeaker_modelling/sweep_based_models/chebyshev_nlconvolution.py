import sumpf
import nlsp
import common
import _common as nlspcommon



def loudspeakerevaluation():
    load = sumpf.modules.SignalFile(filename=common.get_filename("Visaton BF45", "Sweep20", 1),
                                    format=sumpf.modules.SignalFile.WAV_FLOAT)
    excitation = sumpf.modules.SplitSignal(data=load.GetSignal(), channels=[0]).GetOutput()
    response = sumpf.modules.SplitSignal(data=load.GetSignal(), channels=[1]).GetOutput()
    kernel = nlsp.nonlinearconvolution_chebyshev_filter(excitation,response,[20.0,20000.0,branches])
    model = nlsp.HammersteinGroupModel(input_signal=excitation,
                                       nonlinear_functions=nlsp.nonlinearconvolution_chebyshev_nlfunction(branches),
                                       filter_irs=kernel,max_harmonics=range(1,6))
    common.plot.log()
    common.plot.plot(sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),show=False)
    common.plot.plot(sumpf.modules.FourierTransform(response).GetSpectrum())

branches = 5
loudspeakerevaluation()