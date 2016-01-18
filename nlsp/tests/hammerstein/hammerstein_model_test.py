import sumpf
import nlsp
import _common as common
import common.plot as plot
import itertools
import numpy

#include other input and output methods in this testing after debugging the base model
def test_connectors():
    """
    Check whether the input and output connectors are connected properly
    """
    freq = 10000
    s_rate = 48000
    length = s_rate
    model = nlsp.HammersteinModel(nonlin_func=nlsp.NonlinearFunction.power_series(1))
    energy1 = common.calculateenergy(model.GetOutput())
    assert energy1 == [0]
    gen_sine = sumpf.modules.SineWaveGenerator(frequency=freq,
                                          phase=0.0,
                                          samplingrate=s_rate,
                                          length=length).GetSignal()
    prp = sumpf.modules.ChannelDataProperties(signal_length=length,samplingrate=s_rate)
    model.SetInput(gen_sine)
    energy2 = common.calculateenergy(model.GetOutput())
    assert energy2 != energy1
    model.SetInput(sumpf.Signal())
    energy3 = common.calculateenergy(model.GetOutput())
    assert energy3 == energy1
    model.SetInput(gen_sine)
    # model.SetNLFunction(nonlin_func="power")
    # energy4 = common.calculateenergy(model.GetOutput())
    # assert energy4 != energy3
    model.SetFilterIR(sumpf.modules.InverseFourierTransform(sumpf.modules.FilterGenerator
                                                (sumpf.modules.FilterGenerator.BUTTERWORTH(order=5),frequency=freq,
                                                resolution=prp.GetResolution(),
                                                length=prp.GetSpectrumLength()).GetSpectrum()).GetSignal())
    energy5 = common.calculateenergy(model.GetOutput())
    assert energy5 != energy3
    # model.SetMaximumHarmonic(2)
    # energy6 = common.calculateenergy(model.GetOutput())
    # assert energy6 != energy5

def test_linearity_of_model():
    """
    Test the Hammerstein model for linearity for first order nonlinearity block and all pass filter linear block
    """
    gen_sine = sumpf.modules.SineWaveGenerator(frequency=10000.0,
                                      phase=0.0,
                                      samplingrate=48000,
                                      length=48000).GetSignal()
    model = nlsp.HammersteinModel(input_signal=gen_sine,nonlin_func=nlsp.NonlinearFunction.power_series(1))
    energy_ip = common.calculateenergy(gen_sine)
    energy_op = common.calculateenergy(model.GetOutput())
    assert int(energy_ip[0]) == int(energy_op[0])

def test_aliasingtest():
    """
    Test the Aliasing effect in the model. The output freq are calculated theoretically and is compared with the model.
    If input freq is greater than nyquist freq then aliasing occurs because of which frequencies which are not in input
    signal appears in the output. This test tests the aliasing effect. if it fails then there should be freq in the
    output other than the theoretically calculated freq, then there should be some problem in the signal processing
    block
    """
    max_harm = 5
    freq = 20000
    s_rate = 48000
    length = s_rate
    sine_signal = sumpf.modules.SineWaveGenerator(frequency=freq,
                                          phase=0.0,
                                          samplingrate=s_rate,
                                          length=length)
    sine_spec = sumpf.modules.FourierTransform(signal=sine_signal.GetSignal())
    Test_Model_Hammerstein = nlsp.HammersteinModel(input_signal=sine_signal.GetSignal(),
                                                   nonlin_func=nlsp.NonlinearFunction.power_series(max_harm))
    Test_Model_outputsignal = Test_Model_Hammerstein.GetOutput()
    Test_Model_outputspec = sumpf.modules.FourierTransform(Test_Model_outputsignal).GetSpectrum()
    Test_Model_HarmonicFreq = []
    h = common.find_frequencies(Test_Model_outputsignal)
    predicted_freq = common.predictoutputfreq_usingsamplingtheory(freq,max_harm,s_rate)
    assert predicted_freq == h

def test_aliasingtest_comparewithupsampling():
    """
    Test the Aliasing effect in the model. The output freq are calculated by applying the signal to the
    upsampling hammerstein model and is compared with the model.
    If input freq is greater than nyquist freq then aliasing occurs because of which frequencies which are not in input
    signal appears in the output. This test tests the aliasing effect. if it fails then there should be freq in the
    output other than the theoretically calculated freq, then there should be some problem in the signal processing
    block
    """
    max_harm = 2
    frequency = [1000,23000,5222,5698]
    s_rate = 48000
    length = s_rate
    for freq in frequency:
        sine_signal = sumpf.modules.SineWaveGenerator(frequency=freq,
                                              phase=0.0,
                                              samplingrate=s_rate,
                                              length=length)
        sine_spec = sumpf.modules.FourierTransform(signal=sine_signal.GetSignal())
        Test_Model_Hammerstein = nlsp.HammersteinModel(input_signal=sine_signal.GetSignal(),
                                                       nonlin_func=nlsp.NonlinearFunction.power_series(max_harm))
        Test_Model_outputsignal = Test_Model_Hammerstein.GetOutput()
        Test_Model_outputspec = sumpf.modules.FourierTransform(Test_Model_outputsignal).GetSpectrum()
        Test_Model_HarmonicFreq = []
        frequencies = common.find_frequencies(Test_Model_outputsignal)
        predict_freq = common.predictharmonics_usingupsampling([freq],max_harm,s_rate)
        if freq*max_harm < s_rate/2:
            assert frequencies == predict_freq
        else:
            assert frequencies != predict_freq

def test_modelquality():
    """
    Tests the quality of the model. On observing the models it is found that the upsampling hammerstein model doesnot
    produce aliasing effect. But other models produces aliasing. This test makes sure that aliasing will be produced
    in the model if frequency*max_harm is greater than sampling rate
    """
    max_harm = [1, 2, 3, 4, 5]
    frequency = [1000, 5000, 10000, 15000, 23000]
    s_rate = 48000
    length = s_rate

    combinations = list(itertools.product(frequency,max_harm))
    for comb in combinations:
        freq = comb[0]
        harm = comb[1]
        sine_signal = sumpf.modules.SineWaveGenerator(frequency=freq,
                                                  phase=0.0,
                                                  samplingrate=s_rate,
                                                  length=length)
        sine_spec = sumpf.modules.FourierTransform(signal=sine_signal.GetSignal())
        Test_Model_Hammerstein = nlsp.HammersteinModel(input_signal=sine_signal.GetSignal(),
                                                           nonlin_func=nlsp.NonlinearFunction.power_series(harm))
        Test_Model_outputsignal = Test_Model_Hammerstein.GetOutput()
        e = common.calculateenergy(Test_Model_outputsignal)
        h = common.predictharmonics_usingupsampling([freq],harm,s_rate)
        f = common.calculateenergy_atparticularfrequencies(Test_Model_outputsignal,h)
        quality = numpy.sum(f)/numpy.sum(e)
        if freq*harm > s_rate/2:
            assert quality <= 1
        else:
            assert quality == 1
