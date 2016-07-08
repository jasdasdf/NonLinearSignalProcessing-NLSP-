import os
import sumpf
import nlsp
import nlsp.common.plots as plot


def regularizedspectraldivision(input_signal,response):
    """
    regularized spectral division vs normal spectral division
    """
    input_spec = sumpf.modules.FourierTransform(input_signal).GetSpectrum()
    response_spec = sumpf.modules.FourierTransform(response).GetSpectrum()
    normal_tf = sumpf.modules.DivideSpectrums(spectrum1=response_spec, spectrum2=input_spec).GetOutput()
    reg_inv = sumpf.modules.RegularizedSpectrumInversion(spectrum=input_spec,start_frequency=20.0,stop_frequency=20000.0).GetOutput()
    reg_specdivision = sumpf.modules.MultiplySpectrums(spectrum1=reg_inv, spectrum2=response_spec)
    reg_tf = reg_specdivision.GetOutput()
    plot.relabelandplot(input_spec,"input spectrum",show=False)
    plot.relabelandplot(response_spec,"output spectrum",show=False)
    plot.relabelandplot(normal_tf,"transfer function without regularization",show=False)
    plot.relabelandplot(reg_tf,"regularized transfer function",show=True)

def comparereversedandsi():
    sampling_rate = 48000
    length = 2**16
    branches = 5
    excitation = nlsp.NovakSweepGenerator_Sine(start_frequency=20.0,stop_frequency=20000.0,
                                              length=length,sampling_rate=sampling_rate)
    input_signal = excitation.GetOutput()
    input_spec = sumpf.modules.FourierTransform(input_signal).GetSpectrum()
    prp = sumpf.modules.ChannelDataProperties()
    prp.SetSignal(input_signal)
    filter_spec_tofind = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                                   frequency=20.0,transform=True,resolution=prp.GetResolution(),
                                                   length=prp.GetSpectrumLength()).GetSpectrum()
    filter_spec_tofind = [sumpf.modules.InverseFourierTransform(filter_spec_tofind).GetSignal(),]*branches
    ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
    nlsp.plotstft(ref_nlsystem.GetOutput())
    nlsp.plotstft(input_signal)
    response = ref_nlsystem.GetOutput()
    response_spec = sumpf.modules.FourierTransform(response).GetSpectrum()
    reg_inv = sumpf.modules.RegularizedSpectrumInversion(spectrum=input_spec,start_frequency=20.0,stop_frequency=6000.0,epsilon_max=0.1).GetOutput()
    reg_specdivision = sumpf.modules.MultiplySpectrums(spectrum1=reg_inv, spectrum2=response_spec)
    reg_tf = reg_specdivision.GetOutput()
    nl_ir_si = sumpf.modules.InverseFourierTransform(spectrum=reg_tf).GetSignal()

    rev = excitation.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = response_spec / response.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()

    plot.relabelandplot(nl_ir_si,"spectralinversion_ir",show=False)
    plot.relabelandplot(ir_sweep,"reverse_ir",show=True)

def plot_spectrogram():
    sampling_rate = 48000
    length = 2**18
    branches = 5
    excitation = nlsp.NovakSweepGenerator_Sine(start_frequency=20.0,stop_frequency=20000.0,
                                              length=length,sampling_rate=sampling_rate)
    # plot.plot_spectrogram(excitation.GetReversedOutput())
    # plot.plot_spectrogram(excitation.GetOutput())
    nlsp.plotstft(excitation.GetOutput())

def differentdeconcolution():
    sampling_rate = 48000.0
    start_freq = 100.0
    stop_freq = 20000.0
    length = 2**18
    fade_out = 0.00
    fade_in = 0.00
    branches = 5
    sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    sine_f = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= 0.02,fade_in=0.02)

    source_dir = "C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_db/"
    load_sine = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"sine.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    load_sine_f = sumpf.modules.SignalFile(filename=os.path.join(source_dir,"sine_f.npz"), format=sumpf.modules.SignalFile.WAV_FLOAT)
    output_sine = sumpf.modules.SplitSignal(data=load_sine.GetSignal(),channels=[1]).GetOutput()
    output_sine_f = sumpf.modules.SplitSignal(data=load_sine_f.GetSignal(),channels=[1]).GetOutput()

    ir_reverse = nlsp.get_nl_impulse_response(sine,output_sine)
    ir_specinv = nlsp.get_impulse_response(sine.GetOutput(),output_sine,start_freq,stop_freq)
    ir_specinv_fade = nlsp.get_impulse_response(sine_f.GetOutput(),output_sine_f,start_freq,stop_freq)
    plot.relabelandplot(ir_specinv,show=True,label="IR_SpectralInversion")
    plot.relabelandplot(ir_specinv_fade,show=True,label="IR_SpectralInversion_fade")
    plot.relabelandplot(ir_reverse,show=True,label="IR_Reverse")

differentdeconcolution()