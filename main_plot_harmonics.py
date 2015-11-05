import scipy.optimize
import matplotlib.pyplot as pyplot
import math
import numpy
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

def highpass_secondorder(numerator):
    numerator[0] = 1- numerator[0]
    numerator[1] = 2- numerator[1]
    numerator[2] = 1- numerator[2]
    return numerator

def hammerstein(excitation):
    prp = sumpf.modules.ChannelDataProperties(signal_length=len(excitation), samplingrate=excitation.GetSamplingRate())

    lowpass1 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),frequency=140.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    lowpass2 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),frequency=1500.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    lowpass3 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=2),frequency=3000.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()

    highpass = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.CHEBYCHEV1(order=2,ripple=3.0),frequency=140.0,transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()

    model = common.ClippingHammersteinGroupModel(signal=excitation,thresholds_list=[(-0.2,0.2), (-0.5,0.5)],filters=(highpass*lowpass1*lowpass2, highpass*highpass*lowpass3), amplificationfactor=1)
    return model

def plot(data):
    if isinstance(data[0], sumpf.Spectrum):
        outputs = sumpf.modules.MergeSpectrums(spectrums=data).GetOutput()
    else:
        merged = sumpf.modules.MergeSignals(signals=data).GetOutput()
        outputs = sumpf.modules.FourierTransform(signal=merged).GetSpectrum()
#    outputs = sumpf.modules.NormalizeSpectrumToAverage(input=outputs, individual=True).GetOutput()
    common.plot.log()
    common.plot.plot(outputs)

def Comparision(loudspeaker, signaltype, output):
    signal = sumpf.modules.SignalFile(filename=get_filename(loudspeaker, signaltype, 2), format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
    soundpressure = sumpf.modules.SplitSignal(data=signal, channels=[1]).GetOutput()
    voltage = sumpf.modules.SplitSignal(data=signal, channels=[0]).GetOutput()
    measured_harmonics = harmonics(excitation=voltage, response=soundpressure, order=1)
    model = hammerstein(excitation=voltage)
    simulated_harmonics = harmonics(excitation=voltage, response=model.GetOutput(), order=1)
    plot([measured_harmonics, simulated_harmonics])
    merge = sumpf.modules.MergeSignals()
    merge.AddInput(signal=model.GetOutput())
    merge.AddInput(signal=soundpressure)
    merge.AddInput(signal=voltage)
    fft = sumpf.modules.FourierTransform(signal=merge.GetOutput()).GetSpectrum()
    norm_fft = sumpf.modules.NormalizeSpectrumToAverage(input=fft, order=2.0, individual=True).GetOutput() * len(fft)
    ifft = sumpf.modules.InverseFourierTransform(spectrum=norm_fft).GetSignal()
    ifft = sumpf.modules.NormalizeSignal(input=ifft,individual=False).GetOutput()
    sumpf.modules.SignalFile(filename="O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Measurements/Visaton BF45/%s" %output,signal=ifft)


def main():
    Comparision("Visaton BF45", "Sweep18", "Sweepout")
#    Comparision("Visaton BF45", "Noise18", "Noiseout")
#    Comparision("Visaton BF45", "Speech1", "Speechout")
#    Comparision("Visaton BF45", "Music1", "Musicout")

main()

