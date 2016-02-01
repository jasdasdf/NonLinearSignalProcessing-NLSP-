        ##################################################################################
        # power series nonlinear convolution type system identification evaluation script#
        ##################################################################################

# Sweep signal is used as excitation for system identification.
# This input sweep signal is given to the virtual nonlinear system and output is obtained. The input and output is used
#       for power series nonlinear convolution type system identification.
# The system identification identifies the linear block impulse response and the nonlinear block for power nl
#       convolution type system identification is given by power series polynomials.
# The hammerstein group model is constructed using the identified parameters

import sumpf
import nlsp
import common.plot as plot

def findfilter_evaluation(filter_frequencies):
    """
    Evaluation of System Identification method by hgm nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters as
                       linear functions
    inputsignal - sweep signal
    plot - the original filter spectrum and the identified filter spectrum
    expectation - utmost similarity between the two spectrums
    """
    filter_freq = filter_frequencies
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
    nlsystem = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=range(1,branches+1))
    nlsystem.SetInput(input_sweep)
    found_filter_spec = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    for i,foundspec in enumerate(found_filter_spec):
        plot.log()
        plot.plot(sumpf.modules.FourierTransform(foundspec).GetSpectrum(),show=False)
        plot.plot(sumpf.modules.FourierTransform(filter_spec_tofind[i]).GetSpectrum(),show=False)
    plot.show()

def sweep_evaluation(filter_frequencies):
    """
    Evaluation of System Identification method by hgm nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                       as linear functions
    inputsignal - sweep signal
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    filter_freq = filter_frequencies
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
    nlsystem = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                              filter_irs=filter_spec_tofind,
                                              max_harmonics=range(1,branches+1))
    nlsystem.SetInput(input_sweep)
    found_filter_spec = nlsp.nonlinearconvolution_powerseries_filter(input_sweep,nlsystem.GetOutput(),[sweep_start_freq,
                                                                                                     sweep_stop_freq,
                                                                                                     branches])
    hgm = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                              filter_irs=found_filter_spec,
                                              max_harmonics=range(1,branches+1))
    hgm.SetInput(input_sweep)
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(hgm.GetOutput()).GetSpectrum(), show=False)
    plot.plot(sumpf.modules.FourierTransform(nlsystem.GetOutput()).GetSpectrum(), show=True)
    print "Signal to noise ratio of ip: %r and op: %r of powerseries nl convolution method" \
          %(nlsp.get_snr(input_sweep,nlsystem.GetOutput()),
            nlsp.get_snr(input_sweep,hgm.GetOutput()))

def puretone_op_evaluation(filter_frequencies, puretone_freq):
    """
    Evaluation of System Identification method by hgm nl system
    nonlinear system - virtual hammerstein group model with power series polynomials as nl function and bandpass filters
                       as linear functions
    inputsignal - puretone signal mixture
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    filter_freq = filter_frequencies
    ip_freq = puretone_freq
    input_sweep = sumpf.modules.SweepGenerator(start_frequency=sweep_start_freq, stop_frequency=sweep_stop_freq,
                                               samplingrate=sampling_rate, length=sweep_length).GetSignal()
    ip_sine = nlsp.generate_puretones(frequencies=ip_freq, sampling_rate=sampling_rate, length=sweep_length)
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
    output_sweep = nlsp.HammersteinGroupModel_up(input_signal=input_sweep,
                                              nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                              filter_irs=filter_spec,
                                              max_harmonics=range(1,branches+1))
    ref_output = nlsp.HammersteinGroupModel_up(input_signal=ip_sine,
                                          nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(5),
                                          filter_irs=filter_spec,
                                          max_harmonics=range(1,branches+1))
    model_op = nlsp.HammersteinGroupModel_up(input_signal=ip_sine,
                                nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                filter_irs=nlsp.nonlinearconvolution_powerseries_filter(input_sweep,
                                                                                      output_sweep.GetOutput(),
                                                                                      [sweep_start_freq,sweep_stop_freq,branches]),
                                max_harmonics=range(1,branches+1))
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(ref_output.GetOutput()).GetSpectrum(),show=False)
    plot.plot(sumpf.modules.FourierTransform(model_op.GetOutput()).GetSpectrum(),show=True)

def puretone_hardclipping_evaluation(thresholds,puretone_freq):
    """
    Evaluation of System Identification method by hard clipping system
    nonlinear system - virtual clipping systems which hard clips the signal amplitute which are not in the threshold range
    inputsignal - puretone signal mixture
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    threshold = thresholds
    ip_freq = puretone_freq
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length).GetSignal()
    output_sweep = sumpf.modules.ClipSignal(signal=input_sweep,thresholds=threshold).GetOutput()

    h = nlsp.nonlinearconvolution_powerseries_filter(input_sweep=input_sweep, output_sweep=output_sweep,
                                                   prop=[sweep_start_freq,sweep_stop_freq,branches])
    nl = nlsp.nonlinearconvolution_powerseries_nlfunction(branches)
    h_model = nlsp.HammersteinGroupModel_up(nonlinear_functions=nl, filter_irs=h, max_harmonics=range(1,branches+1))
    ip_sine = nlsp.generate_puretones(frequencies=ip_freq, sampling_rate=sampling_rate, length=sweep_length)
    op_sine = sumpf.modules.ClipSignal(signal=ip_sine,thresholds=threshold).GetOutput()
    h_model.SetInput(ip_sine)
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),show=False)
    plot.plot(sumpf.modules.FourierTransform(h_model.GetOutput()).GetSpectrum(),show=True)

def puretone_softclipping_evaluation(thresholds,puretone_freq,power):
    """
    Evaluation of System Identification method by soft clipping system
    nonlinear system - virtual clipping systems which soft clips the signal amplitute which are not in the threshold range
    inputsignal - puretone signal mixture
    plot - the virtual nl system output and the identified nl system output
    expectation - utmost similarity between the two outputs
    """
    threshold = thresholds
    ip_freq = puretone_freq
    clip_power = power
    input_sweep = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=sweep_length).GetSignal()
    output_sweep = nlsp.NLClipSignal(signal=input_sweep,thresholds=threshold,power=clip_power).GetOutput()

    h = nlsp.nonlinearconvolution_powerseries_filter(input_sweep=input_sweep, output_sweep=output_sweep,
                                                   prop=[sweep_start_freq,sweep_stop_freq,branches])
    nl = nlsp.nonlinearconvolution_powerseries_nlfunction(branches)
    h_model = nlsp.HammersteinGroupModel_up(nonlinear_functions=nl, filter_irs=h, max_harmonics=range(1,branches+1))
    ip_sine = nlsp.generate_puretones(frequencies=ip_freq, sampling_rate=sampling_rate, length=sweep_length)
    op_sine = nlsp.NLClipSignal(signal=ip_sine,thresholds=threshold,power=clip_power).GetOutput()
    h_model.SetInput(ip_sine)
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),show=False)
    plot.plot(sumpf.modules.FourierTransform(h_model.GetOutput()).GetSpectrum(),show=True)

def linear_amplification_evaluation(amplification_factor,puretone_freq):
    """
    Evaluation of System Identification method by linear amplification
    nonlinear system - no nonlinearity, linear amplifier as linear system
    inputsignal - puretone signal mixture
    plot - the virtual linear system output and the identified linear system output
    expectation - utmost similarity between the two outputs
    """
    amplification = amplification_factor
    ip_freq = puretone_freq

    input_sweep = sumpf.modules.SweepGenerator(start_frequency=sweep_start_freq, stop_frequency=sweep_stop_freq,
                                               samplingrate=sampling_rate, length=sweep_length).GetSignal()
    output_sweep = sumpf.modules.AmplifySignal(input=input_sweep,factor=amplification).GetOutput()

    h = nlsp.nonlinearconvolution_powerseries_filter(input_sweep=input_sweep,output_sweep=output_sweep,
                                                   prop=[sweep_start_freq,sweep_stop_freq,branches])
    nl = nlsp.nonlinearconvolution_powerseries_nlfunction(branches)
    h_model = nlsp.HammersteinGroupModel_up(nonlinear_functions=nl, filter_irs=h, max_harmonics=range(1,branches+1))
    ip_sine = nlsp.generate_puretones(frequencies=ip_freq, sampling_rate=sampling_rate, length=sweep_length)
    op_sine = sumpf.modules.AmplifySignal(input=ip_sine,factor=amplification).GetOutput()
    h_model.SetInput(ip_sine)
    plot.log()
    plot.plot(sumpf.modules.FourierTransform(op_sine).GetSpectrum(),show=False)
    plot.plot(sumpf.modules.FourierTransform(h_model.GetOutput()).GetSpectrum(),show=True)

sampling_rate = 48000
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
branches = 5
sweep_length = 2**15

findfilter_evaluation(filter_frequencies=(300,800,2000,8000,12000))
sweep_evaluation(filter_frequencies=(300,800,2000,8000,12000))
puretone_op_evaluation(filter_frequencies=(300,800,2000,8000,12000),puretone_freq=(500,1000))
puretone_hardclipping_evaluation(thresholds=[-0.5,0.5],puretone_freq=(500,1000))
puretone_softclipping_evaluation(thresholds=[-0.5,0.5],puretone_freq=(500,1000),power=1/float(3))
linear_amplification_evaluation(amplification_factor=1.0,puretone_freq=(500,1000))

