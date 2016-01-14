import sumpf
import nlsp
import common

frequency = [15000]
max_harm = 2

def PredictHarmonicsUsingUpsamplingHM(frequency,max_harm):

    samplingrate = 48000.0
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
    Test_Model_Hammerstein = nlsp.AliasCompensatingHammersteinModelLowpass(input_signal=sine_combined_signal,
                                                            nonlin_func=nlsp.NonlinearFunction.power_series(max_harm))
    Reference_Model_outputsignal = Reference_Model.GetOutput()
    Test_Model_outputsignal = Test_Model_Hammerstein.GetOutput()
    Reference_Model_outputspec = sumpf.modules.FourierTransform(Reference_Model_outputsignal).GetSpectrum()
    Test_Model_outputspec = sumpf.modules.FourierTransform(Test_Model_outputsignal).GetSpectrum()
    Reference_Model_HarmonicFreq = []
    Test_Model_HarmonicFreq = []
    for c in Reference_Model_outputspec.GetChannels():
        channel_h = []
        for i, s in enumerate(c):
            if abs(s)**2 > 100:
                channel_h.append(i)
        Reference_Model_HarmonicFreq.append(tuple(channel_h))
    print "Reference Model Max harmonics:%d, Input freq:%s, Output freq:%s" %(max_harm,', '.join(map(str, frequency)),', '.join(map(str, Reference_Model_HarmonicFreq)))
    for c in Test_Model_outputspec.GetChannels():
        channel_h = []
        for i, s in enumerate(c):
            if abs(s)**2 > 100:
                channel_h.append(i)
        Test_Model_HarmonicFreq.append(tuple(channel_h))
    print "Test Model Max harmonics     :%d, Input freq:%s, Output freq:%s" %(max_harm,', '.join(map(str, frequency)),', '.join(map(str, Test_Model_HarmonicFreq)))
    common.plot.log()
    common.plot.plot(Reference_Model_outputspec,show=False)
    common.plot.plot(Test_Model_outputspec,show=True)


PredictHarmonicsUsingUpsamplingHM(frequency,max_harm)