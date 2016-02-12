import sumpf
import nlsp
import common
import head_specific

def split_signals():

    loudspeaker = "Visaton BF45"
    sample = ["Sweep16","Sweep18","Sweep20","Speech1","Speech2","Speech3","Music1","Noise18","Noise20"]

    for signal in sample:
        # load loudspeaker measurings
        load_sweep = sumpf.modules.SignalFile(filename=common.get_filename(loudspeaker,signal, 1),
                                        format=sumpf.modules.SignalFile.WAV_FLOAT)
        excitation = sumpf.modules.SplitSignal(data=load_sweep.GetSignal(), channels=[0]).GetOutput()
        save = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/test_signals/%s"%signal,
                                      signal=excitation,format=sumpf.modules.SignalFile.NUMPY_NPZ)


def loudspeakermodel_evaluation():
    loudspeaker = "Visaton BF45"
    sweep = "Sweep20"
    sample = "Speech3"
    # load loudspeaker measurings
    load_sweep = sumpf.modules.SignalFile(filename=common.get_filename(loudspeaker,sweep, 1),
                                    format=sumpf.modules.SignalFile.WAV_FLOAT)
    excitation = sumpf.modules.SplitSignal(data=load_sweep.GetSignal(), channels=[0]).GetOutput()
    response = sumpf.modules.SplitSignal(data=load_sweep.GetSignal(), channels=[1]).GetOutput()

    # identify kernel using nonlinear convolution method
    sweep_start_freq, sweep_stop_freq, sweep_duration = head_specific.get_sweep_properties(excitation)
    sweep_duration = sweep_duration * excitation.GetSamplingRate()
    kernel = nlsp.NLConvolution(input_sweep=excitation, output_sweep=response, sweep_start_freq=sweep_start_freq,
                                sweep_stop_freq=sweep_stop_freq,sweep_length=sweep_duration,branches=branches)
    # kernel = nlsp.NLConvolution(input_sweep=excitation, output_sweep=response, sweep_start_freq=20.0,
    #                             sweep_stop_freq=20000.0,branches=branches)

    # use identified kernel in nl convolution hammerstein model
    ls_model = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                       filter_irs=kernel.GetPower_filter_1(),max_harmonics=range(1,branches+1))

    # load sample to evaluate the loudspeaker model
    load_sample = sumpf.modules.SignalFile(filename=common.get_filename(loudspeaker, sample, 1),
                                          format=sumpf.modules.SignalFile.WAV_FLOAT)
    sample_excitation = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[0]).GetOutput()
    sample_response = sumpf.modules.SplitSignal(data=load_sample.GetSignal(),channels=[1]).GetOutput()
    print len(sample_response),len(excitation)
    if len(sample_excitation) > len(excitation):
        sample_excitation = sumpf.modules.CutSignal(signal=sample_excitation,start=0,stop=len(excitation)).GetOutput()
        sample_response = sumpf.modules.CutSignal(signal=sample_response,start=0,stop=len(excitation)).GetOutput()
    else:
        sample_excitation = nlsp.append_zeros(sample_excitation,length=len(excitation))
        sample_response = nlsp.append_zeros(sample_response,length=len(response))
    ls_model.SetInput(sample_excitation)

    # highpass filter the output of the model to prevent amplification of low freq signals
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(ls_model.GetOutput())
    highpass = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),
                                                      frequency=100.0,transform=True,resolution=prp.GetResolution(),
                                                      length=prp.GetSpectrumLength()).GetSpectrum()
    model_up_highpass = sumpf.modules.MultiplySpectrums(spectrum1=sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),
                                                        spectrum2=highpass).GetOutput()
    model_up_highpass_signal = sumpf.modules.InverseFourierTransform(model_up_highpass).GetSignal()


    # save the output to the directory
    iden = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/NLconvolution/identified",
                                      signal=model_up_highpass_signal,format=sumpf.modules.SignalFile.WAV_FLOAT)
    ref = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/NLconvolution/reference",
                                      signal=sample_response,format=sumpf.modules.SignalFile.WAV_FLOAT)
    inp = sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/recordings/NLconvolution/input",
                                      signal=sample_excitation,format=sumpf.modules.SignalFile.WAV_FLOAT)
    print "SNR between Reference and Identified output Sample: %r" %nlsp.signal_to_noise_ratio_time(sample_response,
                                                                                             model_up_highpass_signal)
    if Plot is True:
        # plot the loudspeaker op against identified op
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),"identified_sample_spectrum",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(sample_response).GetSpectrum(),"reference_sample_spectrum",True)

        # plot the sweep prediction outputs
        ls_model.SetInput(excitation)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(ls_model.GetOutput()).GetSpectrum(),"identified_sweep_spectrum",False)
        nlsp.relabelandplot(sumpf.modules.FourierTransform(response).GetSpectrum(),"reference_sweep_spectrum",True)

    print "SNR between Reference and Identified output Sweep: %r" %nlsp.signal_to_noise_ratio_time(response,ls_model.GetOutput())

branches = 5
Plot = True
split_signals()
# loudspeakermodel_evaluation()