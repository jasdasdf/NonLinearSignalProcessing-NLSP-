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
Speaker = "Visaton BF45"
Signal = 18
plotoutput = False
inital_threshold_decay = 1            # Value to be optimized by alg
initial_threshold_assymetry = 1       # Value to be optimized by alg
branches = 4
start_value = 2                       # Threshold start value

#################################################################

def get_thresholds(branches, start_value, asymmetry, decay):
    thresholds_list = []
    for i in range(branches):
        minimum = -start_value * math.e**-abs(i * decay)
        maximum = (start_value + asymmetry) * math.e**-abs(i * decay)
        thresholds_list.append([minimum, maximum])
    return thresholds_list

threshold = functools.partial(get_thresholds,branches,start_value) # braches, start value, asymmetry

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

def Initial_parameters(length, samplingrate):
    prp = sumpf.modules.ChannelDataProperties(signal_length=length, samplingrate=samplingrate)
    lowpass_filter = sumpf.modules.FilterGenerator.BUTTERWORTH(order=2)
    highpass_filter = sumpf.modules.FilterGenerator.CHEBYCHEV1(order=2,ripple=3.0)
    lowpass1 = sumpf.modules.FilterGenerator(highpass_filter,frequency=140.0,transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    lowpass2 = sumpf.modules.FilterGenerator(lowpass_filter,frequency=300.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    lowpass3 = sumpf.modules.FilterGenerator(lowpass_filter,frequency=200.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    highpass = sumpf.modules.FilterGenerator(highpass_filter,frequency=140.0,transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    initial_thresholds_list = threshold(initial_threshold_assymetry,inital_threshold_decay)
    initial_amplificationfactor = 1
    return lowpass1,lowpass2,lowpass3,highpass,initial_thresholds_list,initial_amplificationfactor,lowpass_filter,highpass_filter

def map_value(value, initial_guess, limits):
	minimum, maximum = limits
	difference = (maximum - minimum)
#	return difference / (1.0 + math.exp(-((value - initial_guess) / difference))) + minimum
	return difference * 0.5 * (math.sin(value) + 1.0) + minimum

def unmap_value(value, initial_guess, limits):
	minimum, maximum = limits
	difference = maximum - minimum
#	return -math.log(difference / (value - minimum) - 1.0) * difference + initial_guess
	return math.asin(2.0 * (value - minimum) / difference - 1.0)

# Get the properties of the recorded excitation and response
length = 2**Signal
samplingrate = 48000
sweep_start_frequency, sweep_stop_frequency, sweep_duration = head_specific.get_sweep_properties(sumpf.modules.SilenceGenerator(length=length, samplingrate=samplingrate).GetSignal())
print "Input sweep prop: startfreq-%f, stopfreq-%f, duration-%f" %(sweep_start_frequency, sweep_stop_frequency, sweep_duration)
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
lowpass1,lowpass2,lowpass3,highpass,initial_thresholds_list,initial_amplificationfactor,lowpass_filter,highpass_filter = Initial_parameters(length,samplingrate)

# print some initial debug information
print "Initial threshold decay       ", inital_threshold_decay
print "Initial threshold assymetry   ", initial_threshold_assymetry
print "Initial thresholds:           ", (initial_thresholds_list)
print "Initial hp coefficients:      ", (highpass_filter.GetCoefficients())
print "Initial lp coefficients:      ", (lowpass_filter.GetCoefficients())

# model for extracting the harmonics of simulated signal
model = common.ClippingHammersteinGroupModel(signal=split_excitation.GetOutput(),thresholds_list=initial_thresholds_list,filters=(highpass,lowpass1,lowpass2,lowpass3),amplificationfactor=initial_amplificationfactor)
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
    merge_ipandop_harmonics = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_withharmonics.GetSpectrum(),tf_simulated_withharmonics.GetSpectrum()]).GetOutput()
    merge_ipandop_fundamental = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_fundamental.GetOutput(),tf_simulated_fundamental.GetOutput()]).GetOutput()
    common.plot.log()
    common.plot.plot(merge_ipandop_fundamental)
    common.plot.plot(merge_ipandop_harmonics)

def errorfunction(parameters):
    # parse the parameters
    threshold_decay    = parameters[0]
    threshold_assymetry= parameters[1]
    numeratorhp    = parameters[2:5]
    denominatorhp  = parameters[5:8]
    numeratorlp    = parameters[8:11]
    denominatorlp  = parameters[11:14]

    # limit the parameters
    threshold_assymetry = map_value(threshold_assymetry,0,[-1,1])
    threshold_decay = map_value(threshold_decay,0,[0,1])

    # calculate the exact values
    thresholds_list = threshold(threshold_assymetry, threshold_decay)

    # print some debug information
    print "threshold decay    ", threshold_decay
    print "threshold assymetry", threshold_assymetry
    print "thresholds:        ", (thresholds_list)
    print "hp parameter:      ", (numeratorhp,denominatorhp)
    print "lp parameter:      ", (numeratorlp,denominatorlp)

    # compute the filters
    prp = sumpf.modules.ChannelDataProperties(signal_length=length, samplingrate=samplingrate)
    lowpass1 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorlp,denominator=denominatorlp),frequency=200.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    lowpass2 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorlp,denominator=denominatorlp),frequency=180.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    lowpass3 = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorlp,denominator=denominatorlp),frequency=3000.0,transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    highpass = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorhp,denominator=denominatorhp),frequency=100.0,transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()

    # update the model
    model.SetParameters(thresholds_list=thresholds_list,
                        filters=(highpass,lowpass1,lowpass2,lowpass3))
    if plotoutput == True:
        merge_ipandop_harmonics = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_withharmonics.GetSpectrum(),tf_simulated_withharmonics.GetSpectrum()]).GetOutput()
        merge_ipandop_fundamental = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_fundamental.GetOutput(),tf_simulated_fundamental.GetOutput()]).GetOutput()
        common.plot.log()
        common.plot.plot(merge_ipandop_fundamental)
        common.plot.plot(merge_ipandop_harmonics)

    # compute an error value
    difference = tf_measured_fundamental.GetOutput() - tf_simulated_fundamental.GetOutput()
    positive = difference * difference
    magnitude = numpy.array(positive.GetMagnitude())
    cropped = magnitude[:, int(round(200.0/positive.GetResolution())):int(round(4000.0/positive.GetResolution()))]
    error = numpy.sum(cropped)
    print "error:        ", error
    print
    return error


def norm_coeff(filter_coefficients,cutoff_frequency):
    result = numpy.zeros(shape=(2,3))
    for i, s in enumerate(filter_coefficients[0]):
        for j, c in enumerate(s):
            result[i][j] = c/(2.0*math.pi*cutoff_frequency**i)
    normalized = numpy.divide(result, result[1][0])
    return list(normalized[0]), list(normalized[1][1:])

lowpass1,lowpass2,lowpass3,highpass,initial_thresholds_list,initial_amplificationfactor,lowpass_filter,highpass_filter

numeratorhp, denominatorhp = (highpass_filter.GetCoefficients()[0][0]+[0]*3)[:3], highpass_filter.GetCoefficients()[0][1]
numeratorlp, denominatorlp = (lowpass_filter.GetCoefficients()[0][0]+[0]*3)[:3], lowpass_filter.GetCoefficients()[0][1]
threshold_decay = [inital_threshold_decay]
threshold_assymetry = [initial_threshold_assymetry]

# print some debug information
print "Parameter Vector for optimizing (decay,assymetry,hp,lp):", (threshold_decay+threshold_assymetry+numeratorhp+denominatorhp+numeratorlp+denominatorlp)

# Optimize the parameters by reducing the error function
# method = 'Powell'
method = 'L-BFGS-B'
result = scipy.optimize.minimize(errorfunction,
                                (threshold_decay+threshold_assymetry+numeratorhp+denominatorhp+numeratorlp+denominatorlp),
                                 method= method)

# print result and plot output
print result
merge_ipandop_harmonics = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_withharmonics.GetSpectrum(),tf_simulated_withharmonics.GetSpectrum()]).GetOutput()
merge_ipandop_fundamental = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_fundamental.GetOutput(),tf_simulated_fundamental.GetOutput()]).GetOutput()
common.plot.log()
common.plot.plot(merge_ipandop_fundamental)
common.plot.plot(merge_ipandop_harmonics)