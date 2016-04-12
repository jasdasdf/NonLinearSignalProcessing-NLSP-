import sumpf
import nlsp
import nlsp.common.plots as plot


def audio_evaluation(input_generator,branches,iden_method,Plot):

    input_signal = input_generator.GetOutput()
    filter_spec_tofind = nlsp.create_bpfilter([1000,2000,4000,8000,16000],input_signal)
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))

    excitation = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Speech3.npz",
                                              format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
    ref_nlsystem.SetInput(excitation)
    iden_nlsystem.SetInput(excitation)
    ref = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Ref",
                                      signal=ref_nlsystem.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    iden = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/nl_recordings/virtual/Iden",
                                      signal=iden_nlsystem.GetOutput(),format=sumpf.modules.SignalFile.WAV_FLOAT)
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

def novak_ieee_evaluation(input_generator,branches,iden_method,Plot):
    branches = 2
    input_signal = input_generator.GetOutput()
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(input_signal)
    hp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=10),
                                                       frequency=500.0,transform=True,resolution=prp.GetResolution(),
                                                       length=prp.GetSpectrumLength()).GetSpectrum()
    lp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=10),
                                                       frequency=1000.0,transform=False,resolution=prp.GetResolution(),
                                                       length=prp.GetSpectrumLength()).GetSpectrum()
    filter_spec_tofind = [sumpf.modules.InverseFourierTransform(hp).GetSignal(),
                          sumpf.modules.InverseFourierTransform(lp).GetSignal()]
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=[nlsp.function_factory.power_series(1),
                                                                      nlsp.function_factory.power_series(3)],
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,3))

    found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
    iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,3))
    if Plot is True:
        plot.relabelandplotphase(sumpf.modules.FourierTransform(ref_nlsystem.GetOutput()).GetSpectrum(),"Reference System",show=False)
        plot.relabelandplotphase(sumpf.modules.FourierTransform(iden_nlsystem.GetOutput()).GetSpectrum(),"Identified System",show=True)
    print "SNR between Reference and Identified output without overlapping filters: %r" %nlsp.snr(ref_nlsystem.GetOutput(),
                                                                                             iden_nlsystem.GetOutput())

audio_evaluation()
novak_ieee_evaluation()