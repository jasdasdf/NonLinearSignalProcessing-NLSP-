import sumpf
import common
import head_specific

def get_filename(speaker, smd, repetition):
    """
    available speakers: "Visaton BF45", "70s"
    """
    path = "O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Measurements/%s/output/%s_SMD%i_Index%i_TimeSignal"
    smds = {"Noise120s": 4,
            "Sweep16": 5,
            "Sweep18": 6,
            "Sweep20": 7,
            "Noise18": 8,
            "Noise20": 9,
            "Music1": 10,
            "Speech1": 11,
            "Speech2": 12,
            "Speech3": 13}
    return path % (speaker, speaker, smds[smd], repetition)

def hammerstein(excitation):
    prp = sumpf.modules.ChannelDataProperties(signal_length=len(excitation), samplingrate=excitation.GetSamplingRate())
    hp200 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.CHEBYCHEV1(order=2, ripple=3.0),frequency=140.0,transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
#    hp200_2 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.CHEBYCHEV1(order=2, ripple=0.5),frequency=140.0,transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()

    lowpass = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),frequency=200.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    highpass = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),frequency=200.0,transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
#    bandstop = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BANDSTOP(q_factor=1.0),frequency=6100.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()

    model = common.ClippingHammersteinGroupModel(signal=excitation,thresholds_list=[(-10.0, 10.0), (-0.2,0.2), (-0.5,0.5), (-10.0, 10.0)],filters=(hp200, hp200*lowpass*lowpass, hp200*highpass, highpass), amplificationfactor=1)
#    model = common.ClippingHammersteinGroupModel(signal=excitation,thresholds_list=[(-0.2,0.2), (-0.5,0.5)],filters=(hp200*lowpass*lowpass, hp200*highpass), amplificationfactor=1)
#    model = common.ClippingHammersteinGroupModel(signal=model.GetOutput(),thresholds_list=[(-1,1),(-1,1)],filters=(hp200_2*lowpass*lowpass,bandstop), amplificationfactor=1)
    return model

def plotdata(data):
    if isinstance(data[0], sumpf.Spectrum):
        outputs = sumpf.modules.MergeSpectrums(spectrums=data).GetOutput()
    else:
        merged = sumpf.modules.MergeSignals(signals=data).GetOutput()
        outputs = sumpf.modules.FourierTransform(signal=merged).GetSpectrum()
#    outputs = sumpf.modules.NormalizeSpectrumToAverage(input=outputs, individual=True).GetOutput()
    common.plot.log()
    common.plot.plot(outputs)

def get_harmonics(transferfunction, n):
    impulse = sumpf.modules.InverseFourierTransform(spectrum=transferfunction).GetSignal()
    sweep_start_frequency, sweep_stop_frequency, sweep_duration = head_specific.get_sweep_properties(impulse)
    harmonicimpulse = sumpf.modules.FindHarmonicImpulseResponse(impulse_response=impulse, harmonic_order=n, sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration).GetHarmonicImpulseResponse()
    harmonicimpulse1resampled = sumpf.modules.ResampleSignal(signal=harmonicimpulse, samplingrate=impulse.GetSamplingRate()).GetOutput()
    silencelength = len(impulse)-len(harmonicimpulse1resampled)
    silence = sumpf.modules.SilenceGenerator(samplingrate=impulse.GetSamplingRate(), length=silencelength).GetSignal()
    concatenated = sumpf.modules.ConcatenateSignals(signal1=harmonicimpulse1resampled, signal2=silence).GetOutput()
    harmonicspectrum = sumpf.modules.FourierTransform(signal=concatenated).GetSpectrum()
    return harmonicspectrum

def harmonics(excitation, response, order=3):
    excitation_spectrum = sumpf.modules.FourierTransform(excitation).GetSpectrum()
    response_spectrum = sumpf.modules.FourierTransform(response).GetSpectrum()
    inversion = sumpf.modules.RegularizedSpectrumInversion(spectrum=excitation_spectrum, start_frequency=20.0, stop_frequency=20000.0, transition_length=100,epsilon_max=0.1).GetOutput()
    transferfunction = response_spectrum * inversion
    merger = sumpf.modules.MergeSpectrums()
    merger.AddInput(transferfunction)
    for i in range(2,order+1):
        merger.AddInput(get_harmonics(transferfunction, i))
    return merger.GetOutput()
