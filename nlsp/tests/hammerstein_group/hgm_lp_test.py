import numpy
import sumpf
import nlsp

def test_puretone():
    """
    Tests whether hammerstein group model produces reliable result for pure sine tone.
    The pure sine tone is given to hammerstein model of different maximum harmonic alias compensation and the output
    freq are found for each branch. Then the same pure sine tone is given to hammerstein group model and the output
    is observed. It should have the same frequencies which we get from individual hammerstein model.
    """
    max_harm = [1,2,3,4,5]
    freq = 8000
    s_rate = 48000
    length = s_rate
    ip_sine_signal = sumpf.modules.SineWaveGenerator(frequency=freq,
                                          phase=0.0,
                                          samplingrate=s_rate,
                                          length=length).GetSignal()
    h = []
    for harm in max_harm:
        Test_Model_Hammerstein = nlsp.AliasingCompensatedHM_lowpass(input_signal=ip_sine_signal,
                                                       nonlin_func=nlsp.function_factory.power_series(harm),
                                                       max_harm=harm)
        Test_Model_outputsignal = Test_Model_Hammerstein.GetOutput()
        h.append(nlsp.find_frequencies(Test_Model_outputsignal))
    Test_model_freq = sorted(list(set([item for sublist in h for item in sublist])))
    imp = sumpf.modules.ImpulseGenerator(samplingrate=s_rate, length=length).GetSignal()
    hammerstein_group = nlsp.HammersteinGroupModel_lp(input_signal=ip_sine_signal,
                                                   nonlinear_functions=(nlsp.function_factory.power_series(max_harm[0]),
                                                   nlsp.function_factory.power_series(max_harm[1]),
                                                   nlsp.function_factory.power_series(max_harm[2]),
                                                   nlsp.function_factory.power_series(max_harm[3]),
                                                   nlsp.function_factory.power_series(max_harm[4])),
                                                   filter_irs=(imp,)*len(max_harm),
                                                   max_harmonics=max_harm)
    Test_groupmodel_freq = nlsp.find_frequencies(hammerstein_group.GetOutput())
    assert Test_groupmodel_freq == Test_model_freq

def test_aliasing():
    """
    Tests whether aliasing is present in the hammerstein group model.
    The pure sine tone is given to the model and the output frequencies found in all the branches are found. The energy
    of these frequencies in the output of the hammerstein group model is calculated. If there is no aliasing then this
    should be equal to the total energy of the output signal.
    """
    max_harm = [1,2,3,4,5]
    freq = 5000
    s_rate = 48000
    length = s_rate
    ip_sine_signal = sumpf.modules.SineWaveGenerator(frequency=freq,
                                          phase=0.0,
                                          samplingrate=s_rate,
                                          length=length).GetSignal()
    h = []
    for harm in max_harm:
        Test_Model_Hammerstein = nlsp.AliasingCompensatedHM_lowpass(input_signal=ip_sine_signal,
                                                       nonlin_func=nlsp.function_factory.power_series(harm),
                                                       max_harm=harm)
        Test_Model_outputsignal = Test_Model_Hammerstein.GetOutput()
        h.append(nlsp.find_frequencies(Test_Model_outputsignal))
    Test_model_freq = sorted(list(set([item for sublist in h for item in sublist])))
    imp = sumpf.modules.ImpulseGenerator(samplingrate=s_rate, length=length).GetSignal()
    hammerstein_group = nlsp.HammersteinGroupModel_lp(input_signal=ip_sine_signal,
                                                   nonlinear_functions=(nlsp.function_factory.power_series(max_harm[0]),
                                                   nlsp.function_factory.power_series(max_harm[1]),
                                                   nlsp.function_factory.power_series(max_harm[2]),
                                                   nlsp.function_factory.power_series(max_harm[3]),
                                                   nlsp.function_factory.power_series(max_harm[4])),
                                                   filter_irs=(imp,)*len(max_harm),
                                                   max_harmonics=max_harm)
    Test_groupmodel_energy_freq = nlsp.calculateenergy_atparticularfrequencies(hammerstein_group.GetOutput(),
                                                                            frequencies=Test_model_freq)
    Test_groupmodel_energy_all = nlsp.calculateenergy_freq(hammerstein_group.GetOutput())
    assert int(numpy.sum(Test_groupmodel_energy_all)) == int(numpy.sum(Test_groupmodel_energy_freq))

def test_energy():
    """
    Test of the relation between the energy of hammerstein group model and simple hammerstein model.
    (a + b)^2 <= 2a^2 + 2b^2
    The above relation is proved for the model using this test
    """
    max_harm = [1]*2
    freq = 5000
    s_rate = 48000
    length = s_rate
    ip_sine_signal = sumpf.modules.SineWaveGenerator(frequency=freq,
                                          phase=0.0,
                                          samplingrate=s_rate,
                                          length=length).GetSignal()
    imp = sumpf.modules.ImpulseGenerator(samplingrate=s_rate, length=length).GetSignal()
    e = []
    for harm in max_harm:
        Test_Model_Hammerstein = nlsp.AliasingCompensatedHM_lowpass(input_signal=ip_sine_signal,
                                                       nonlin_func=nlsp.function_factory.power_series(harm),
                                                       filter_impulseresponse=imp,
                                                       max_harm=harm)
        Test_Model_outputsignal = Test_Model_Hammerstein.GetOutput()
        e.append(numpy.multiply(nlsp.calculateenergy_freq(Test_Model_outputsignal),2))
    hammerstein_group = nlsp.HammersteinGroupModel_lp(input_signal=ip_sine_signal,
                                                   nonlinear_functions=(nlsp.function_factory.power_series(max_harm[0]),
                                                                        )*len(max_harm),
                                                   filter_irs=(imp,)*len(max_harm),
                                                   max_harmonics=max_harm)
    e_g = nlsp.calculateenergy_freq(hammerstein_group.GetOutput())
    assert float(numpy.sum(e_g)) <= float(numpy.sum(e))