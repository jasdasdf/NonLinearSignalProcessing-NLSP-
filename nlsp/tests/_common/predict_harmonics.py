import sumpf
import nlsp

def predictharmonics_usingupsampling(frequency,max_harm,samplingrate):
    """
    :param frequency: list of frequencies, the superposition of this list of frequencies is given to the nonlinear
                        system whose harmonics is to be predicted
    :param max_harm:  the maximum harmonics which will be established by the nonlinear system
    :return: the list of frequencies which should appear in the output. These harmonics are not calculated
                mathematically but it uses the Upsampling model to predict the harmonics
    """
    length = samplingrate
    sine_signal_array = []
    sine_spec_array = []
    sine_combined_signal = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=samplingrate,length=length).GetSignal()
    for freq in range(0,len(frequency)):
        sine_signal = sumpf.modules.SineWaveGenerator(frequency=frequency[freq],
                                              phase=0.0,
                                              samplingrate=samplingrate,
                                              length=length)
        sine_spec = sumpf.modules.FourierTransform(signal=sine_signal.GetSignal())
        sine_signal_array.append(sine_signal.GetSignal())
        sine_spec_array.append(sine_spec.GetSpectrum())
        sine_combined_signal = sine_combined_signal + sine_signal.GetSignal()
    sine_combined_spec = sumpf.modules.FourierTransform(signal=sine_combined_signal).GetSpectrum()
    Reference_Model = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=sine_combined_signal,
                                                            nonlin_func=nlsp.NonlinearFunction.power_series(max_harm))
    Reference_Model_outputsignal = Reference_Model.GetOutput()
    Reference_Model_outputspec = sumpf.modules.FourierTransform(Reference_Model_outputsignal).GetSpectrum()
    Reference_Model_HarmonicFreq = []
    for c in Reference_Model_outputspec.GetChannels():
        channel_h = []
        for i, s in enumerate(c):
            if abs(s)**2 > 100:
                channel_h.append(i)
        Reference_Model_HarmonicFreq.append(channel_h)
    h = [item for sublist in Reference_Model_HarmonicFreq for item in sublist]
    return h