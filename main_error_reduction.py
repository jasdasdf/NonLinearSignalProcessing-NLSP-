import math
import time
import os.path
import subprocess
import scipy.optimize
import numpy
import sumpf
import common
import head_specific
from desktopmagic.screengrab_win32 import (getDisplayRects, saveScreenToBmp, saveRectToBmp, getScreenAsImage, getRectAsImage, getDisplaysAsImages)


degree = 18
length = 2**degree
samplingrate = 48000
sweep_start_frequency, sweep_stop_frequency, sweep_duration = head_specific.get_sweep_properties(sumpf.modules.SilenceGenerator(length=length, samplingrate=samplingrate).GetSignal())
print sweep_start_frequency, sweep_stop_frequency, sweep_duration
print sweep_start_frequency, sweep_stop_frequency, sweep_duration

load = sumpf.modules.SignalFile(filename=common.get_filename("Visaton BF45", "Sweep%i" % degree, 1),format=sumpf.modules.SignalFile.WAV_FLOAT)
split_excitation = sumpf.modules.SplitSignal(channels=[0])
sumpf.connect(load.GetSignal, split_excitation.SetInput)
split_response = sumpf.modules.SplitSignal(channels=[1])

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
fft_measured = sumpf.modules.FourierTransform()
sumpf.connect(merge_measuered.GetOutput, fft_measured.SetSignal)

model = common.hammerstein(split_excitation.GetOutput())
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
fft_simulated = sumpf.modules.FourierTransform()
sumpf.connect(merge_simulated.GetOutput, fft_simulated.SetSignal)

def errorfunction(parameters):
    # parse the parameters
    thresholds1    = parameters[0:2]
    numerator11    = parameters[2:5]
    denominator11  = [1.0]
    denominator12  = [1.0]
    denominator21  = [1.0]
    denominator22  = [1.0]
    denominator11.extend(parameters[5:7])
    numerator12    = parameters[7:10]
    denominator12.extend(parameters[10:12])
    thresholds2    = parameters[12:14]
    numerator21    = parameters[14:17]
    denominator21.extend(parameters[17:19])
    numerator22    = parameters[19:22]
    denominator22.extend(parameters[22:24])

    # print some debug information
    print "thresholds:        ", (thresholds1, thresholds2)
    print "filter1 parameter: ", (numerator11,denominator11,numerator12,denominator12)
    print "filter2 parameter: ", (numerator21,denominator21,numerator22,denominator22)

    # compute the filters
    prp = sumpf.modules.ChannelDataProperties(signal_length=length, samplingrate=samplingrate)
    filter1 = sumpf.modules.FilterWithCoefficients(coefficients=[(numerator11, denominator11), (numerator12, denominator12)],frequency=1.0/(2.0*math.pi), transform=False, resolution=prp.GetResolution(), length=prp.GetSpectrumLength()).GetSpectrum()
    filter2 = sumpf.modules.FilterWithCoefficients(coefficients=[(numerator21, denominator21), (numerator22, denominator22)],frequency=1.0/(2.0*math.pi), transform=False, resolution=prp.GetResolution(), length=prp.GetSpectrumLength()).GetSpectrum()
    filter3 = 
    filter4 =
    # update the model
    model.SetParameters(thresholds_list=(thresholds1, thresholds2),
                        filters=(filter1,filter2))

    # compute an error value
    difference = fft_measured.GetSpectrum() - fft_simulated.GetSpectrum()
    positive = difference * difference
    magnitude = numpy.array(positive.GetMagnitude())
    cropped = magnitude[:, int(round(200.0/positive.GetResolution())):int(round(5000.0/positive.GetResolution()))]
    error = numpy.sum(cropped)
    print "error:             ", error
    print
    return error




def norm_coeff(filter_coefficients,cutoff_frequency):
    result = numpy.zeros(shape=(2,3))
    for i, s in enumerate(filter_coefficients[0]):
        for j, c in enumerate(s):
            result[i][j] = c/(2.0*math.pi*cutoff_frequency**i)
    normalized = numpy.divide(result, result[1][0])
    return list(normalized[0]), list(normalized[1][1:])

thresholds1 = [-0.2,0.2]
numerator11, denominator11 = [ 2.02016467,  3.45383741, -0.0045483 ], [-196.07832435820882, -361.87548246847717]
numerator12, denominator12 = [ 2.02016467,  3.45383741, -0.0045483 ], [-196.07832435820882, -361.87548246847717]
thresholds2 = [-0.5,0.5]
numerator21, denominator21 = [ 37.13605964,   4.8003011 ,  -0.0437737 ], [815.16126868499975, 1159.5476657350441]
numerator22, denominator22 = [ 37.13605964,   4.8003011 ,  -0.0437737 ], [815.16126868499975, 1159.547665745044]

turns = 0

method = 'L-BFGS-B'
result = scipy.optimize.minimize(errorfunction,
                                 (thresholds1+numerator11+denominator11+numerator12+denominator12+
                                  thresholds2+numerator21+denominator21+numerator22+denominator22),
                                 method= method)
print result

split_fundamental_measured = sumpf.modules.SplitSpectrum(channels=[0])
split_fundamental_simulated = sumpf.modules.SplitSpectrum(channels=[0])
sumpf.connect(fft_measured.GetSpectrum, split_fundamental_measured.SetInput)
sumpf.connect(fft_simulated.GetSpectrum, split_fundamental_simulated.SetInput)
merge_output = sumpf.modules.MergeSpectrums(spectrums=[fft_measured.GetSpectrum(),fft_simulated.GetSpectrum()]).GetOutput()
merge_outputh = sumpf.modules.MergeSpectrums(spectrums=[split_fundamental_simulated.GetOutput(),split_fundamental_measured.GetOutput()]).GetOutput()
common.plot.log()
common.plot.plot(merge_output)
common.plot.plot(merge_outputh)
