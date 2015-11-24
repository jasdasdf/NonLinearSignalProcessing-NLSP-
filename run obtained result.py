import math
import time
import os.path
import subprocess
import functools
import scipy.optimize
import numpy
import sumpf
import common
import head_specific

################################ Inputs #########################

Dir = "C:/Users/diplomand.8/Desktop/output_logs/"
Speaker = "Visaton BF45"
Signal = 18
plotoutput = True
start_value = 2.0
branches = 7

#################################################################

def Read_log():
    filename = "%s_%d_%d.txt" %(Speaker,Signal,branches)
    log_file = os.path.join(Dir,filename)
    filters = []
    threshold_decay = []
    threshold_assymetry = []
    for i,line in enumerate(reversed(open(log_file).readlines())):
        if i < branches:
            filters.append(line.split())
        elif i == branches+1:
            threshold_decay.append(line.split())
        elif i == branches:
            threshold_assymetry.append(line.split())
    coefficients = []
    for j in range(0,branches):
        coefficients.append([float(i) for i in (filters[j][0][:-1].split(','))])
    threshold_decay = [float(i) for i in threshold_decay[0]]
    threshold_assymetry = [float(i) for i in threshold_assymetry[0]]
    return threshold_decay,threshold_assymetry,coefficients


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

def get_thresholds(branches, start_value, asymmetry, decay):
    thresholds_list = []
    for i in range(branches):
        minimum = -start_value * math.e**-abs(i * decay)
        maximum = (start_value + asymmetry) * math.e**-abs(i * decay)
        thresholds_list.append([minimum, maximum])
    return thresholds_list

threshold = functools.partial(get_thresholds,branches,start_value) # braches, start value, asymmetry

def Initial_parameters(length, samplingrate):
    threshold_decay,threshold_assymetry,coefficients = Read_log()

    prp = sumpf.modules.ChannelDataProperties(signal_length=length, samplingrate=samplingrate)
    filter1 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=coefficients[6][:3],denominator=coefficients[6][3:]),transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter2 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=coefficients[5][:3],denominator=coefficients[5][3:]),transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter3 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=coefficients[4][:3],denominator=coefficients[4][3:]),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter4 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=coefficients[3][:3],denominator=coefficients[3][3:]),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter5 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=coefficients[2][:3],denominator=coefficients[2][3:]),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter6 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=coefficients[1][:3],denominator=coefficients[1][3:]),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter7 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=coefficients[0][:3],denominator=coefficients[0][3:]),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()

    filter_lists = [filter1,filter2,filter3,filter4,filter5,filter6,filter7]
    thresholds_list = threshold(threshold_assymetry[0],threshold_decay[0])
    amplificationfactor = 1
    return filter_lists,thresholds_list,amplificationfactor

# Get the properties of the recorded excitation and response
length = 2**Signal
samplingrate = 48000
sweep_start_frequency, sweep_stop_frequency, sweep_duration = head_specific.get_sweep_properties(sumpf.modules.SilenceGenerator(length=length, samplingrate=samplingrate).GetSignal())
load = sumpf.modules.SignalFile(filename=common.get_filename(Speaker, "Sweep%i" % Signal, 1),format=sumpf.modules.SignalFile.WAV_FLOAT)
split_excitation = sumpf.modules.SplitSignal(channels=[0])
sumpf.connect(load.GetSignal, split_excitation.SetInput)
split_response = sumpf.modules.SplitSignal(channels=[1])

# Model for extracting the harmonics of the recorded signal
sumpf.connect(load.GetSignal, split_response.SetInput)
fft_excitation = sumpf.modules.FourierTransform()
sumpf.connect(split_excitation.GetOutput, fft_excitation.SetSignal)
fft_response = sumpf.modules.FourierTransform()
sumpf.connect(split_response.GetOutput, fft_response.SetSignal)
inversion = sumpf.modules.RegularizedSpectrumInversion(start_frequency=max(sweep_start_frequency*4.0, 20.0),stop_frequency=sweep_stop_frequency/4.0,transition_length=100,epsilon_max=0.1)
sumpf.connect(fft_excitation.GetSpectrum,inversion.SetSpectrum)
tf_measured = sumpf.modules.MultiplySpectrums()
sumpf.connect(inversion.GetOutput, tf_measured.SetInput1)
sumpf.connect(fft_response.GetSpectrum,tf_measured.SetInput2)
ir_measured = sumpf.modules.InverseFourierTransform()
sumpf.connect(tf_measured.GetOutput,ir_measured.SetSpectrum)
h1_measured = sumpf.modules.CutSignal(start=0, stop=4096)
sumpf.connect(ir_measured.GetSignal,h1_measured.SetInput)
h2_measured = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=2,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
sumpf.connect(ir_measured.GetSignal,h2_measured.SetImpulseResponse)
h3_measured = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=3,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
sumpf.connect(ir_measured.GetSignal,h3_measured.SetImpulseResponse)
h4_measured = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=4,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
sumpf.connect(ir_measured.GetSignal,h4_measured.SetImpulseResponse)
h5_measured = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=5,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
sumpf.connect(ir_measured.GetSignal,h5_measured.SetImpulseResponse)
merge_measuered = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
resample1_measured = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h1_measured.GetOutput,resample1_measured.SetInput)
resample2_measured = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h2_measured.GetHarmonicImpulseResponse,resample2_measured.SetInput)
resample3_measured = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h3_measured.GetHarmonicImpulseResponse,resample3_measured.SetInput)
resample4_measured = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h4_measured.GetHarmonicImpulseResponse,resample4_measured.SetInput)
resample5_measured = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h5_measured.GetHarmonicImpulseResponse,resample5_measured.SetInput)
sumpf.connect(resample1_measured.GetOutput, merge_measuered.AddInput)
sumpf.connect(resample2_measured.GetOutput, merge_measuered.AddInput)
sumpf.connect(resample3_measured.GetOutput, merge_measuered.AddInput)
sumpf.connect(resample4_measured.GetOutput, merge_measuered.AddInput)
sumpf.connect(resample5_measured.GetOutput, merge_measuered.AddInput)
tf_measured_withharmonics = sumpf.modules.FourierTransform()
sumpf.connect(merge_measuered.GetOutput, tf_measured_withharmonics.SetSignal)
tf_measured_fundamental = sumpf.modules.SplitSpectrum(channels=[0])
sumpf.connect(tf_measured_withharmonics.GetSpectrum, tf_measured_fundamental.SetInput)

# Get the Initial parameters of the model
filter_lists,thresholds_list,amplificationfactor = Initial_parameters(length,samplingrate)

# model for extracting the harmonics of simulated signal
model = common.ClippingHammersteinGroupModel(signal=split_excitation.GetOutput(),thresholds_list=thresholds_list,filters=filter_lists,amplificationfactor=amplificationfactor)
sumpf.connect(split_excitation.GetOutput, model.SetInput)
fft_model = sumpf.modules.FourierTransform()
sumpf.connect(model.GetOutput, fft_model.SetSignal)
tf_simulated = sumpf.modules.MultiplySpectrums()
sumpf.connect(inversion.GetOutput, tf_simulated.SetInput1)
sumpf.connect(fft_model.GetSpectrum,tf_simulated.SetInput2)
ir_simulated = sumpf.modules.InverseFourierTransform()
sumpf.connect(tf_simulated.GetOutput,ir_simulated.SetSpectrum)
h1_simulated = sumpf.modules.CutSignal(start=0, stop=4096)
sumpf.connect(ir_simulated.GetSignal,h1_simulated.SetInput)
h2_simulated = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=2,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
sumpf.connect(ir_simulated.GetSignal,h2_simulated.SetImpulseResponse)
h3_simulated = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=3,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
sumpf.connect(ir_simulated.GetSignal,h3_simulated.SetImpulseResponse)
h4_simulated = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=4,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
sumpf.connect(ir_simulated.GetSignal,h4_simulated.SetImpulseResponse)
h5_simulated = sumpf.modules.FindHarmonicImpulseResponse(harmonic_order=5,sweep_start_frequency=sweep_start_frequency, sweep_stop_frequency=sweep_stop_frequency, sweep_duration=sweep_duration)
sumpf.connect(ir_simulated.GetSignal,h5_simulated.SetImpulseResponse)
resample1_simulated = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h1_simulated.GetOutput,resample1_simulated.SetInput)
resample2_simulated = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h2_simulated.GetHarmonicImpulseResponse,resample2_simulated.SetInput)
resample3_simulated = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h3_simulated.GetHarmonicImpulseResponse,resample3_simulated.SetInput)
resample4_simulated = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h4_simulated.GetHarmonicImpulseResponse,resample4_simulated.SetInput)
resample5_simulated = sumpf.modules.ResampleSignal(samplingrate=load.GetSamplingRate())
sumpf.connect(h5_simulated.GetHarmonicImpulseResponse,resample5_simulated.SetInput)
merge_simulated = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
sumpf.connect(resample1_simulated.GetOutput, merge_simulated.AddInput)
sumpf.connect(resample2_simulated.GetOutput, merge_simulated.AddInput)
sumpf.connect(resample3_simulated.GetOutput, merge_simulated.AddInput)
sumpf.connect(resample4_simulated.GetOutput, merge_simulated.AddInput)
sumpf.connect(resample5_simulated.GetOutput, merge_simulated.AddInput)
tf_simulated_withharmonics = sumpf.modules.FourierTransform()
sumpf.connect(merge_simulated.GetOutput, tf_simulated_withharmonics.SetSignal)
tf_simulated_fundamental = sumpf.modules.SplitSpectrum(channels=[0])
sumpf.connect(tf_simulated_withharmonics.GetSpectrum, tf_simulated_fundamental.SetInput)

if plotoutput == True:
    merge_ipandop = sumpf.modules.MergeSpectrums(spectrums=[tf_measured.GetOutput(),tf_simulated.GetOutput()]).GetOutput()
    merge_ipandop_harmonics = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_withharmonics.GetSpectrum(),tf_simulated_withharmonics.GetSpectrum()]).GetOutput()
    merge_ipandop_fundamental = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_fundamental.GetOutput(),tf_simulated_fundamental.GetOutput()]).GetOutput()
    common.plot.log()
    common.plot.plot(merge_ipandop)
    common.plot.plot(merge_ipandop_fundamental)
    common.plot.plot(merge_ipandop_harmonics)
