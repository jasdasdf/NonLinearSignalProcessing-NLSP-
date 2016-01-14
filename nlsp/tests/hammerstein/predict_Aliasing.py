import sumpf
import nlsp
import common
import numpy

frequency = 23000.0
max_harm = 5
samplingrate = 48000.0

def PredictAliasingusingSamplingTheorem(frequency,max_harm):

    length = samplingrate
    sine_signal = sumpf.modules.SineWaveGenerator(frequency=frequency,
                                          phase=0.0,
                                          samplingrate=samplingrate,
                                          length=length)
    sine_spec = sumpf.modules.FourierTransform(signal=sine_signal.GetSignal())
    Test_Model_Hammerstein = nlsp.HammersteinModel(input_signal=sine_signal.GetSignal(),
                                                            nonlin_func=nlsp.NonlinearFunction.power_series(max_harm))
    Test_Model_outputsignal = Test_Model_Hammerstein.GetOutput()
    Test_Model_outputspec = sumpf.modules.FourierTransform(Test_Model_outputsignal).GetSpectrum()
    Test_Model_HarmonicFreq = []
    for c in Test_Model_outputspec.GetChannels():
        channel_h = []
        for i, s in enumerate(c):
            if abs(s)**2 > 100:
                channel_h.append(i)
        Test_Model_HarmonicFreq.append(tuple(channel_h))
    print "Test Model Max harmonics:%d, Input freq:%d, Output freq:%s" %(max_harm,frequency,', '.join(map(str, Test_Model_HarmonicFreq)))
    if frequency > (samplingrate/2)*max_harm:
        print "No aliasing below Nyquist frequency"
    else:
        x = []
        for sample in range(-max_harm,max_harm+1,1):
            x.extend([(sample*2*samplingrate/2-frequency,sample*samplingrate+frequency)])
        freq_duplicates = sorted(x)
        if max_harm%2 == 0:
            harm_order = [x for x in range(max_harm) if x%2 == 0]
            harm_order.append(max_harm)
        else:
            harm_order = [x for x in range(max_harm) if x%2 == 1]
            harm_order.append(max_harm)
        f = []
        for freq in freq_duplicates:
            for harm in harm_order:
                f.append(freq[0]-(harm-1)*frequency)
                f.append(freq[1]+(harm-1)*frequency)
        h = filter(lambda x: x>-10 and x<24000,sorted(f))
        print "Predicted aliasing frequencies:%s" %(', '.join(map(str, h)))
    common.plot.log()
    common.plot.plot(Test_Model_outputspec,show=True)

PredictAliasingusingSamplingTheorem(frequency,max_harm)

