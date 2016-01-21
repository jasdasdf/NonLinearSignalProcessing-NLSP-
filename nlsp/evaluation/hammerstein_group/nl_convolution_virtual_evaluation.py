import sumpf
import nlsp
import common.plot as plot
import _common as common

def clipping_evaluation():
    """
    Evaluation of the Nonlinear convolution identification method of nonlinear system by simulating a clipping system.
    The clipping system is assumed as a nonlinear system and a sweep signal is generated and is given to this system.
    The input and output of this clipping system is given to nonlinear convolution type of system identification and the
    filter impulse response and the nonlinear functions are obtained.
    These parameters are given to the Hammerstein group model to simulate the system. This system is evaluated by giving
    a pure sine tone to the clipping system and this hammerstein group model and the outputs of both systems are
    evaluated for performance
    """
    sampling_rate = 48000
    threshold = [-0.5,0.5]
    length = 2**18
    ip_freq = 2000
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    output_sweep = sumpf.modules.ClipSignal(signal=input_sweep,thresholds=threshold).GetOutput()

    h = nlsp.nonlinearconvolution_identification_filter(input_sweep=input_sweep,output_sweep=output_sweep)
    nl = nlsp.nonlinearconvolution_identification_nlfunction()

    h_model = nlsp.HammersteinGroupModel(nonlinear_functions=nl, filter_irs=h, max_harmonics=(1,2,3,4,5))

    ip_sine = sumpf.modules.SineWaveGenerator(frequency=ip_freq,
                                          phase=0.0,
                                          samplingrate=sampling_rate,
                                          length=length).GetSignal()

    op_sine = sumpf.modules.ClipSignal(signal=ip_sine,thresholds=threshold).GetOutput()
    h_model.SetInput(ip_sine)
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),show=False)
    plot.plot(sumpf.modules.FourierTransform(h_model.GetOutput()).GetSpectrum(),show=True)

def amplification_evaluation():
    """
    Evaluation of the Nonlinear convolution identification method of nonlinear system by simulating a amplification
    system. The amplification system is assumed as a nonlinear system and a sweep signal is generated and is given to
    this system. The input and output of this amplification system is given to nonlinear convolution type of system
    identification and the filter impulse response and the nonlinear functions are obtained.
    These parameters are given to the Hammerstein group model to simulate the system. This system is evaluated by giving
    a pure sine tone to the amplification system and this hammerstein group model and the outputs of both systems are
    evaluated for performance
    """
    sampling_rate = 48000
    amplification = 2
    length = 2**18
    ip_freq = 2000
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    output_sweep = sumpf.modules.AmplifySignal(input=input_sweep,factor=amplification).GetOutput()

    h = nlsp.nonlinearconvolution_identification_filter(input_sweep=input_sweep,output_sweep=output_sweep)
    nl = nlsp.nonlinearconvolution_identification_nlfunction()

    h_model = nlsp.HammersteinGroupModel(nonlinear_functions=nl, filter_irs=h, max_harmonics=(1,2,3,4,5))

    ip_sine = sumpf.modules.SineWaveGenerator(frequency=ip_freq,
                                          phase=0.0,
                                          samplingrate=sampling_rate,
                                          length=length).GetSignal()

    op_sine = sumpf.modules.AmplifySignal(input=ip_sine,factor=amplification).GetOutput()
    h_model.SetInput(ip_sine)
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),show=False)
    plot.plot(sumpf.modules.FourierTransform(h_model.GetOutput()).GetSpectrum(),show=True)

def filtering_evaluation():
    """
    Evaluation of the Nonlinear convolution identification method of nonlinear system by simulating a lowpass filtering
    system. The lowpass filtering system is assumed as a nonlinear system and a sweep signal is generated and is given
    to this system. The input and output of this lowpassfiltering system is given to nonlinear convolution type of
    system identification and the filter impulse response and the nonlinear functions are obtained.
    These parameters are given to the Hammerstein group model to simulate the system. This system is evaluated by giving
    a pure sine tone to the lowpass filtering system and this hammerstein group model and the outputs of both systems
    are evaluated for performance
    """
    sampling_rate = 48000
    filter_lp = 3000
    length = 2**18
    ip_freq = 2000
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSignal(input_sweep)
    filter =  sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                            frequency=filter_lp,
                                            resolution=ip_prp.GetResolution(),
                                            length=ip_prp.GetSpectrumLength()).GetSpectrum()
    output_sweep = sumpf.modules.MultiplySpectrums(spectrum1=filter,
                                        spectrum2=sumpf.modules.FourierTransform(input_sweep).GetSpectrum()).GetOutput()

    h = nlsp.nonlinearconvolution_identification_filter(input_sweep=input_sweep,output_sweep=output_sweep)
    nl = nlsp.nonlinearconvolution_identification_nlfunction()

    h_model = nlsp.HammersteinGroupModel(nonlinear_functions=nl, filter_irs=h, max_harmonics=(1,2,3,4,5))

    ip_sine = sumpf.modules.SineWaveGenerator(frequency=ip_freq,
                                          phase=0.0,
                                          samplingrate=sampling_rate,
                                          length=length).GetSignal()

    op_sine = sumpf.modules.MultiplySpectrums(spectrum1=filter,
                                        spectrum2=sumpf.modules.FourierTransform(input_sweep).GetSpectrum()).GetOutput()
    h_model.SetInput(ip_sine)
    plot.log()
    plot.plot(op_sine,show=False)
    plot.plot(sumpf.modules.FourierTransform(h_model.GetOutput()).GetSpectrum(),show=True)

clipping_evaluation()
amplification_evaluation()
filtering_evaluation()

