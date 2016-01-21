import sumpf
import nlsp

def nonlinearconvolution_identification_filter(input_sweep, output_sweep):
    """
    Function to find the filter impulse response of the hammerstein group model using Nonlinear convolution method.
    It is used for nonlinear system identification.
    This function computes the impulse response of the nonlinear system by multiplying the transfer function of the
    output sweep and the regularized spectral inversion of the input sweep. The regularized spectral inversion makes
    sure that the low magnitude frequencies in the input signal is not amplified unanticipatedly due to division in
    frequency domain.
    Then the transfer function is inverse transformed to get the impulse response of the nonlinear system.
    From the nonlinear system impulse response the impulse response of the harmonics are seperated. The higher order
    harmonics impulse response are found in the noncausal part. Since we have calculated the impulse response from the
    frequency domain, it appears in the end of the impulse response due to circular convolution.
    Then the transfer function of the harmonics impulse response is calculated and the mathematical calculation which is
    specified by Farina in Nonlinear convolution paper is performed to find the transfer function of filters which shall
    be used in hammerstein group model. Then it is transformed to time domain and returned.
    The mathematical functions are performed by using the sumpf classes.
    :param input_sweep: the input sweep signal which is given to the nonlinear system
    :param output_sweep: the output signal which is observed from the nonlinear system
    :return: the impulse response of the filters of hammerstein group model
    """
    if isinstance(input_sweep ,(sumpf.Signal)):
        ip_s = input_sweep
        ip = sumpf.modules.FourierTransform(signal=input_sweep).GetSpectrum()
    else:
        ip_s = sumpf.modules.InverseFourierTransform(spectrum=input_sweep).GetSignal()
        ip = input_sweep
    if isinstance(output_sweep ,(sumpf.Signal)):
        op = sumpf.modules.FourierTransform(signal=output_sweep).GetSpectrum()
    else:
        op = output_sweep
    spec_inversion = sumpf.modules.RegularizedSpectrumInversion(spectrum=ip).GetOutput()
    mul = sumpf.modules.MultiplySpectrums(spectrum1=spec_inversion, spectrum2=op).GetOutput()
    it = sumpf.modules.InverseFourierTransform(spectrum=mul).GetSignal()
    direct_ir = sumpf.modules.CutSignal(signal=it,start=0,stop=2**12).GetOutput()
    merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    merger.AddInput(direct_ir)
    for i in range(4):
        split_harm = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=it,
                                                               harmonic_order=i+2).GetHarmonicImpulseResponse()
        resampler = sumpf.modules.ResampleSignal(signal=split_harm, samplingrate=ip_s.GetSamplingRate()).GetOutput()
        merger.AddInput(resampler)
    harm_spec = sumpf.modules.FourierTransform(signal=merger.GetOutput()).GetSpectrum()
    harmonics = []
    for i in range(len(harm_spec.GetChannels())):
        split =  sumpf.modules.SplitSpectrum(data=harm_spec,channels=[i]).GetOutput()
        harmonics.append(split)
    H = []
    H.append(harmonics[0] + 3*harmonics[2] +5*harmonics[4])
    H.append(sumpf.modules.AmplifySpectrum(input=harmonics[1],factor=2j).GetOutput() +
             sumpf.modules.AmplifySpectrum(input=harmonics[3],factor=8j).GetOutput())
    H.append(-4*harmonics[2] - 20*harmonics[4])
    H.append(sumpf.modules.AmplifySpectrum(input=harmonics[3],factor=-8j).GetOutput())
    H.append(16*harmonics[4])
    h = []
    for kernel in H:
        ift = sumpf.modules.InverseFourierTransform(spectrum=kernel).GetSignal()
        h.append(ift)
    return h

def nonlinearconvolution_identification_nlfunction():
    """
    This function returns the nonlinear function to the nonlinear blocks of the hammerstein group model.
    In nonlinear convolution method the nonlinear function is defined by power series expansion, Hence it returns
    the power series expansion functions.
    The power series expansion is done by using nlsp classes.
    :return: the nonlinear functions to the hammerstein group model
    """
    nl = []
    for i in range(5):
        nl.append(nlsp.function_factory.power_series(i+1))
    return nl