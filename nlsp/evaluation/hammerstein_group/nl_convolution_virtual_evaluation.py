import sumpf
import nlsp
import common.plot as plot
import _common as common

sampling_rate = 48000
threshold = [-0.6,0.6]
length = 2**18
ip_freq = 2000

def clipping_evaluation():
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    output_sweep = sumpf.modules.ClipSignal(signal=input_sweep,thresholds=threshold).GetOutput()

    h = nlsp.nonlinearconvolution_identification(input_sweep=input_sweep,output_sweep=output_sweep)

    h_model = nlsp.HammersteinGroupModel(nonlinear_functions=(nlsp.function_factory.power_series(1),
                                                                  nlsp.function_factory.power_series(2),
                                                                  nlsp.function_factory.power_series(3),
                                                                  nlsp.function_factory.power_series(4),
                                                                  nlsp.function_factory.power_series(5)),
                                        filter_irs=h,max_harmonics=(1,2,3,4,5))

    ip_sine = sumpf.modules.SineWaveGenerator(frequency=ip_freq,
                                          phase=0.0,
                                          samplingrate=sampling_rate,
                                          length=length).GetSignal()

    op_sine = sumpf.modules.ClipSignal(signal=ip_sine,thresholds=threshold).GetOutput()
    h_model.SetInput(ip_sine)
    x = common.find_frequencies(h_model.GetOutput(),magnitude=500)
    y = common.find_frequencies(op_sine)
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),show=False)
    plot.plot(sumpf.modules.FourierTransform(h_model.GetOutput()).GetSpectrum(),show=True)

clipping_evaluation()