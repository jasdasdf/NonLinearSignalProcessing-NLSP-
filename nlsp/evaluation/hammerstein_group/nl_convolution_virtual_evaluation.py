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
    length = 2**15
    ip_freq = 2000
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    output_sweep = sumpf.modules.ClipSignal(signal=input_sweep,thresholds=threshold).GetOutput()

    h = nlsp.nonlinearconvolution_identification_filter(input_sweep=input_sweep,output_sweep=output_sweep)
    nl = nlsp.nonlinearconvolution_identification_nlfunction(5)

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
    length = 2**15
    ip_freq = 2000
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    output_sweep = sumpf.modules.AmplifySignal(input=input_sweep,factor=amplification).GetOutput()

    h = nlsp.nonlinearconvolution_identification_filter(input_sweep=input_sweep,output_sweep=output_sweep)
    nl = nlsp.nonlinearconvolution_identification_nlfunction(5)

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
    length = 2**15
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
    nl = nlsp.nonlinearconvolution_identification_nlfunction(5)

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

def polynomial_op_evaluation():
    """
    Evaluation of Nonlinear convolution method by comparing the outputs.
    A Nonlinear system is constructed using hammerstein group models with power series expansion as nonlinear function
    and certain lowpass filters as linear blocks.
    Sweep signal is given to this nonlinear system and output is observed. These input and output signals are given to
    the Nonlinear convolution type system identification to identify the filters.
    The identified filter impulse response is used to construct a hammerstein group model. A pure tone is given to both
    nonlinear system and model and output is evaluated.
    We expect comparable outputs.
    """
    sampling_rate = 48000
    filter_freq = (4000,8000,10000,15000,20000)
    length = 2**15
    ip_freq = 2000
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    ip_sine = sumpf.modules.SineWaveGenerator(frequency=ip_freq,
                                              phase=0.0,
                                              samplingrate=sampling_rate,
                                              length=length).GetSignal()
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSignal(input_sweep)
    filter_spec = []
    for frequency in filter_freq:
        op = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                                frequency=frequency,
                                                resolution=ip_prp.GetResolution(),
                                                length=ip_prp.GetSpectrumLength()).GetSpectrum()
        op_s = sumpf.modules.InverseFourierTransform(op).GetSignal()
        filter_spec.append(op_s)
    output_sweep = nlsp.HammersteinGroupModel(input_signal=input_sweep,
                                              nonlinear_functions=nlsp.nonlinearconvolution_identification_nlfunction(5),
                                              filter_irs=filter_spec,
                                              max_harmonics=(1,2,3,4,5))
    ref_output = nlsp.HammersteinGroupModel(input_signal=ip_sine,
                                          nonlinear_functions=nlsp.nonlinearconvolution_identification_nlfunction(5),
                                          filter_irs=filter_spec,
                                          max_harmonics=(1,2,3,4,5))
    model_op = nlsp.HammersteinGroupModel(input_signal=ip_sine,
                                nonlinear_functions=nlsp.nonlinearconvolution_identification_nlfunction(5),
                                filter_irs=nlsp.nonlinearconvolution_identification_filter(input_sweep,output_sweep.GetOutput()),
                                max_harmonics=(1,2,3,4,5))
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(ref_output.GetOutput()).GetSpectrum(),show=False)
    plot.plot(sumpf.modules.FourierTransform(model_op.GetOutput()).GetSpectrum(),show=True)


def polynomial_filter_evaluation():
    """
    Evaluation of Nonlinear convolution method by identification of filter.
    A Nonlinear system is constructed using hammerstein group models with power series expansion as nonlinear function
    and certain bandpass filters as linear blocks.
    Sweep signal is given to this nonlinear system and output is observed. These input and output signals are given to
    the Nonlinear convolution type system identification.
    We expect the Nonlinear convolution method identifies the spectrum of the filters.
    :return:
    """
    sampling_rate = 48000
    filter_freq = (100,500,1500,5000,15000)
    sweep_start_freq = 20.0
    sweep_stop_freq = 20000.0
    sweep_length = 2**15
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length,
                                               start_frequency=sweep_start_freq,
                                               stop_frequency=sweep_stop_freq).GetSignal()
    ip_prp = sumpf.modules.ChannelDataProperties()
    ip_prp.SetSignal(input_sweep)
    filter_spec_tofind = []
    for freq in filter_freq:
        spec =  (sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                            frequency=freq,
                                            resolution=ip_prp.GetResolution(),
                                            length=ip_prp.GetSpectrumLength()).GetSpectrum())*\
                (sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                            frequency=freq/2,transform=True,
                                            resolution=ip_prp.GetResolution(),
                                            length=ip_prp.GetSpectrumLength()).GetSpectrum())
        filter_spec_tofind.append(sumpf.modules.InverseFourierTransform(spec).GetSignal())
    nlsystem = nlsp.HammersteinGroupModel(nonlinear_functions=nlsp.nonlinearconvolution_identification_nlfunction(5),
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=(1,2,3,4,5))
    nlsystem.SetInput(input_sweep)
    found_filter_spec = nlsp.nonlinearconvolution_identification_filter(input_sweep,nlsystem.GetOutput())
    for i,foundspec in enumerate(found_filter_spec):
        plot.log()
        plot.plot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),show=False)
        plot.plot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),show=False)
    plot.show()

def nonlinear_clipping_evaluation():
    """
    Evaluation of the Nonlinear convolution identification method of nonlinear system by simulating a nonlinear
    clipping system. The clipping system is assumed as a nonlinear system and a sweep signal is generated and is given
    to this system. The input and output of this clipping system is given to nonlinear convolution type of system
    identification and the filter impulse response and the nonlinear functions are obtained.
    These parameters are given to the Hammerstein group model to simulate the system. This system is evaluated by giving
    a pure sine tone to the clipping system and this hammerstein group model and the outputs of both systems are
    evaluated for performance
    """
    sampling_rate = 48000
    threshold = [-1,1]
    length = 2**15
    ip_freq = 2000
    power = 1/float(3)
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    output_sweep = nlsp.NLClipSignal(signal=input_sweep,thresholds=threshold,power=power).GetOutput()

    h = nlsp.nonlinearconvolution_identification_filter(input_sweep=input_sweep,output_sweep=output_sweep)
    nl = nlsp.nonlinearconvolution_identification_nlfunction(5)

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


clipping_evaluation()
polynomial_filter_evaluation()
polynomial_op_evaluation()
filtering_evaluation()
amplification_evaluation()
clipping_evaluation()
nonlinear_clipping_evaluation()