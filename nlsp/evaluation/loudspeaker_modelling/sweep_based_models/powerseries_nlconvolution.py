import sumpf
import nlsp
import common

def loudspeakerevaluation():

    # load loudspeaker measurings
    load = sumpf.modules.SignalFile(filename=common.get_filename("Visaton BF45", "Sweep20", 1),
                                    format=sumpf.modules.SignalFile.WAV_FLOAT)
    excitation = sumpf.modules.SplitSignal(data=load.GetSignal(), channels=[0]).GetOutput()
    response = sumpf.modules.SplitSignal(data=load.GetSignal(), channels=[1]).GetOutput()
    load_music = sumpf.modules.SignalFile(filename=common.get_filename("Visaton BF45", "Speech3", 1),
                                          format=sumpf.modules.SignalFile.WAV_FLOAT)
    music_excitation = sumpf.modules.SplitSignal(data=load_music.GetSignal(),channels=[0]).GetOutput()
    music_response = sumpf.modules.SplitSignal(data=load_music.GetSignal(),channels=[1]).GetOutput()
    print len(music_excitation),len(excitation)
    if len(music_excitation) > len(excitation):
        music_excitation = sumpf.modules.CutSignal(signal=music_excitation,start=0,stop=len(excitation)).GetOutput()
        music_response = sumpf.modules.CutSignal(signal=music_response,start=0,stop=len(excitation)).GetOutput()
    else:
        music_excitation = nlsp.append_zeros(music_excitation,length=len(excitation))
        music_response = nlsp.append_zeros(music_response,length=len(response))

    # identify kernel using nonlinear convolution method
    kernel = nlsp.nonlinearconvolution_powerseries_debug(excitation,response,[20.0,20000.0,branches])

    # use identified kernel in nl convolution hammerstein model
    model = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                       filter_irs=kernel,max_harmonics=range(1,branches+1))

    # model = nlsp.HammersteinGroupModel_lp(nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
    #                                filter_irs=kernel,max_harmonics=range(1,branches+1),
    #                                filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
    #                                attenuation=0.0001)

    # model = nlsp.HammersteinGroupModel(nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
    #                                filter_irs=kernel)
    model.SetInput(music_excitation)
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(model.GetOutput())

    # highpass filter the output of the model to prevent amplification of low freq signals
    highpass = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),
                                                      frequency=100.0,transform=True,resolution=prp.GetResolution(),
                                                      length=prp.GetSpectrumLength()).GetSpectrum()
    model_up_highpass = sumpf.modules.MultiplySpectrums(spectrum1=sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),
                                                        spectrum2=highpass).GetOutput()
    model_up_highpass_signal = sumpf.modules.InverseFourierTransform(model_up_highpass).GetSignal()

    # save the output to the directory
    iden = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Plots/NLconvolutionHGM/iden_speech2",
                                      signal=model_up_highpass_signal,format=sumpf.modules.SignalFile.WAV_FLOAT)
    ref = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Plots/NLconvolutionHGM/ref_speech2",
                                      signal=music_response,format=sumpf.modules.SignalFile.WAV_FLOAT)
    inp = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Plots/NLconvolutionHGM/inp_speech2",
                                      signal=music_excitation,format=sumpf.modules.SignalFile.WAV_FLOAT)

    # plot the loudspeaker op against identified op
    # common.plot.log()
    # common.plot.plot(sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),show=False)
    # common.plot.plot(sumpf.modules.FourierTransform(music_response).GetSpectrum(),show=True)

    # plot the sweep prediction outputs
    common.plot.log()
    model.SetInput(excitation)
    common.plot.plot(sumpf.modules.FourierTransform(response).GetSpectrum(),show=False)
    common.plot.plot(sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),show=True)

branches = 5
loudspeakerevaluation()