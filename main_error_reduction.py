import math
import time
import os.path
import subprocess
import functools
import matplotlib.pyplot as plt
import scipy.optimize
import numpy
import sumpf
import common
import head_specific

################################ Inputs #########################

Dir = "C:/Users/diplomand.8/Desktop/Logesh_Masterthesis/output_logs/new/"                                    # Output directory for logs
Speaker = "Visaton BF45"                                                             # Speaker used
Signal = 18                                                                          # Length of signal samples 2**Signal
plotoutput = False                                                                   # True if to plot tf in every iteration
branches = 5                                                                         # Number of branches in the model
start_value = 0.8                                                                    # Threshold start value
method = 'Nelder-Mead'                                                               # Nelder-Mead,Powell,L-BFGS-B
output_filename = "%s_%d_%d_%s_%f.txt" %(Speaker,Signal,branches,method,start_value) # Output log file

#################################################################

initial_amplification_factor = 1                                                     # amplification factor of the model
chebyshev_ripple = 3.0                                                               # ripple for chebyshev filter
inital_threshold_decay = 0.1                                                         # Initial decay value which will be optimized by the algorithm
initial_threshold_assymetry = 0                                                      # Initial threshold assymetry value which will be optimized by the algorithm
assymetry_limits = [-0.5,0.5]                                                            # Assymetry value limits
decay_limits = [0,0.3]
output_file = os.path.join(Dir,output_filename)
if not os.path.exists(output_file):
    file(output_file, 'w').close()
#################################################################

def get_thresholds(branches, start_value, asymmetry, decay):
    thresholds_list = []
    for i in range(branches):
        minimum = -start_value * math.e**-abs(i * decay)
        maximum = (start_value + asymmetry**i) * math.e**-abs(i * decay)
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
    butterworth_filter = sumpf.modules.FilterGenerator.BUTTERWORTH(order=2)
    chebyshev1_filter = sumpf.modules.FilterGenerator.CHEBYCHEV1(order=2,ripple=chebyshev_ripple)
    filtercb = sumpf.modules.FilterGenerator(chebyshev1_filter,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filterbw = sumpf.modules.FilterGenerator(butterworth_filter,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    initial_thresholds_list = threshold(initial_threshold_assymetry,inital_threshold_decay)
    filter_seq = []
    for i in range(0,branches):
        filter_seq.append(filterbw)
    return filter_seq,initial_thresholds_list,butterworth_filter,chebyshev1_filter

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

def errorfunction(parameters):
    # parse the parameters
    threshold_decay    = parameters[0]
    threshold_assymetry= parameters[1]
    numeratorbw1    = parameters[2:5]
    denominatorbw1  = parameters[5:8]
    numeratorbw2    = parameters[8:11]
    denominatorbw2  = parameters[11:14]
    numeratorbw3    = parameters[14:17]
    denominatorbw3  = parameters[17:20]
    numeratorbw4    = parameters[20:23]
    denominatorbw4  = parameters[23:26]
    numeratorbw5    = parameters[26:29]
    denominatorbw5  = parameters[29:32]
    numeratorcb1    = parameters[32:35]
    denominatorcb1  = parameters[35:38]
    numeratorcb2    = parameters[38:41]
    denominatorcb2  = parameters[41:44]
    numeratorcb3    = parameters[44:47]
    denominatorcb3  = parameters[47:50]
    numeratorcb4    = parameters[50:53]
    denominatorcb4  = parameters[53:56]
    numeratorcb5    = parameters[56:59]
    denominatorcb5  = parameters[59:62]

    # limit the parameters
    threshold_assymetry = map_value(threshold_assymetry,0,assymetry_limits)
    threshold_decay = map_value(threshold_decay,0,decay_limits)

    # calculate the exact values
    thresholds_list = threshold(threshold_assymetry, threshold_decay)

    # compute the filters
    prp = sumpf.modules.ChannelDataProperties(signal_length=length, samplingrate=samplingrate)
    filter1hp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorcb1,denominator=denominatorcb1),transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter2hp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorcb2,denominator=denominatorcb2),transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter3hp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorcb3,denominator=denominatorcb3),transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter4hp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorcb4,denominator=denominatorcb4),transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter5hp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorcb5,denominator=denominatorcb5),transform=True,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter1lp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorbw1,denominator=denominatorbw1),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter2lp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorbw2,denominator=denominatorbw2),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter3lp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorbw3,denominator=denominatorbw3),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter4lp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorbw4,denominator=denominatorbw4),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()
    filter5lp = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.TRANSFERFUNCTION(numerator=numeratorbw5,denominator=denominatorbw5),transform=False,length=prp.GetSpectrumLength(),resolution=prp.GetResolution()).GetSpectrum()

    # update the model
    prp = sumpf.modules.ChannelDataProperties(signal_length=length, samplingrate=samplingrate)
    highpass = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.CHEBYCHEV1(order=2,ripple=chebyshev_ripple),frequency=150.0,transform=True,resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
    model.SetParameters(thresholds_list=thresholds_list,
                        nonlinearfilters=(filter1hp*filter1lp,filter2hp*filter2lp,filter3hp*filter3lp,filter4hp*filter4lp,filter5hp*filter5lp))

   # print model parameters
    print "Speaker and input   ", Speaker,Signal,branches
    print "threshold decay     ", threshold_decay
    print "threshold assymetry ", threshold_assymetry
    print "thresholds:         ", thresholds_list
    print "filter1hp parameter:  ", numeratorcb1,denominatorcb1
    print "filter2hp parameter:  ", numeratorcb2,denominatorcb2
    print "filter3hp parameter:  ", numeratorcb3,denominatorcb3
    print "filter4hp parameter:  ", numeratorcb4,denominatorcb4
    print "filter5hp parameter:  ", numeratorcb5,denominatorcb5
    print "filter1lp parameter:  ", numeratorbw1,denominatorbw1
    print "filter2lp parameter:  ", numeratorbw2,denominatorbw2
    print "filter3lp parameter:  ", numeratorbw3,denominatorbw3
    print "filter4lp parameter:  ", numeratorbw4,denominatorbw4
    print "filter5lp parameter:  ", numeratorbw5,denominatorbw5
    print "output file:        ", output_filename
    print "filter combinations filter1hp*filter1lp,filter2hp*filter2lp,filter3hp*filter3lp,filter4hp*filter4lp,filter5hp*filter5lp",


    # plot the spectrum
    if plotoutput == True:
        merge_ipandop = sumpf.modules.MergeSpectrums(spectrums=[tf_measured.GetOutput(),tf_simulated.GetOutput()]).GetOutput()
        merge_ipandop_harmonics = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_withharmonics.GetSpectrum(),tf_simulated_withharmonics.GetSpectrum()]).GetOutput()
        merge_ipandop_fundamental = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_fundamental.GetOutput(),tf_simulated_fundamental.GetOutput()]).GetOutput()
        common.plot.log()
        common.plot.plot(merge_ipandop)
        common.plot.plot(merge_ipandop_fundamental)
        common.plot.plot(merge_ipandop_harmonics)

    # compute an error value
    difference = tf_measured_withharmonics.GetSpectrum() - tf_simulated_withharmonics.GetSpectrum()
    positive = difference * difference
    magnitude = numpy.array(positive.GetMagnitude())
    cropped = magnitude[:, int(round(50.0/positive.GetResolution())):int(round(1000.0/positive.GetResolution()))]
    exp = numpy.exp(cropped)
    errorexp = numpy.sum(exp)
    error = numpy.sum(cropped)
    print "\nerrorexp:        ", errorexp
    print "error   :        ", error
    print

    f = open(output_file,'a')
    f.write(str(threshold_decay)+'\n')
    f.write(str(threshold_assymetry)+'\n')
    f.writelines(["%f," % float(item)  for item in numeratorcb1])
    f.writelines(["%f," % float(item)  for item in denominatorcb1])
    f.write('highpass,')
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorcb2])
    f.writelines(["%f," % float(item)  for item in denominatorcb2])
    f.write('highpass,')
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorcb3])
    f.writelines(["%f," % float(item)  for item in denominatorcb3])
    f.write('highpass,')
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorcb4])
    f.writelines(["%f," % float(item)  for item in denominatorcb4])
    f.write('highpass,')
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorcb5])
    f.writelines(["%f," % float(item)  for item in denominatorcb5])
    f.write('highpass,')
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorbw1])
    f.writelines(["%f," % float(item)  for item in denominatorbw1])
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorbw2])
    f.writelines(["%f," % float(item)  for item in denominatorbw2])
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorbw3])
    f.writelines(["%f," % float(item)  for item in denominatorbw3])
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorbw4])
    f.writelines(["%f," % float(item)  for item in denominatorbw4])
    f.write('\n')
    f.writelines(["%f," % float(item)  for item in numeratorbw5])
    f.writelines(["%f," % float(item)  for item in denominatorbw5])
    f.write('\n')
    f.write('errorexp:%f,error:%f'%(errorexp,error))
    f.write('\n')
    f.write("filter combinations filter1hp*filter1lp,filter2hp*filter2lp,filter3hp*filter3lp,filter4hp*filter4lp,filter5hp*filter5lp")
    f.write('\n')
    f.close()

    return errorexp


def norm_coeff(filter_coefficients,cutoff_frequency):
    result = numpy.zeros(shape=(2,3))
    for i, s in enumerate(filter_coefficients[0]):
        for j, c in enumerate(s):
            result[i][j] = c/(2.0*math.pi*cutoff_frequency**i)
    normalized = numpy.divide(result, result[1][0])
    return list(normalized[0]), list(normalized[1][1:])


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
filter_seq,initial_thresholds_list,butterworth_filter,chebyshev1_filter = Initial_parameters(length,samplingrate)

# print some initial debug information
print "Initial threshold decay       ", inital_threshold_decay
print "Initial threshold assymetry   ", initial_threshold_assymetry
print "Initial thresholds:           ", (initial_thresholds_list)
print "Initial Butterworth coefficients:      ", (butterworth_filter.GetCoefficients())
print "Initial Chebyshev1 coefficients :      ", (chebyshev1_filter.GetCoefficients())

# model for extracting the harmonics of simulated signal
prp = sumpf.modules.ChannelDataProperties(signal_length=length, samplingrate=samplingrate)
highpass = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.CHEBYCHEV1(order=2,ripple=chebyshev_ripple),frequency=150.0,transform=True,resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
model = common.ClippingHammersteinGroupModelWithCascadedLinearity(signal=split_excitation.GetOutput(),thresholds_list=initial_thresholds_list,nonlinearfilters=filter_seq,amplificationfactor=initial_amplification_factor,linearfilter=highpass)
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

numeratorbw1, denominatorbw1 = (butterworth_filter.GetCoefficients()[0][0]+[0]*3)[:3], butterworth_filter.GetCoefficients()[0][1]
numeratorbw2, denominatorbw2 = (butterworth_filter.GetCoefficients()[0][0]+[0]*3)[:3], butterworth_filter.GetCoefficients()[0][1]
numeratorbw3, denominatorbw3 = (butterworth_filter.GetCoefficients()[0][0]+[0]*3)[:3], butterworth_filter.GetCoefficients()[0][1]
numeratorbw4, denominatorbw4 = (butterworth_filter.GetCoefficients()[0][0]+[0]*3)[:3], butterworth_filter.GetCoefficients()[0][1]
numeratorbw5, denominatorbw5 = (butterworth_filter.GetCoefficients()[0][0]+[0]*3)[:3], butterworth_filter.GetCoefficients()[0][1]
numeratorcb1, denominatorcb1 = (chebyshev1_filter.GetCoefficients()[0][0]+[0]*3)[:3], chebyshev1_filter.GetCoefficients()[0][1]
numeratorcb2, denominatorcb2 = (chebyshev1_filter.GetCoefficients()[0][0]+[0]*3)[:3], chebyshev1_filter.GetCoefficients()[0][1]
numeratorcb3, denominatorcb3 = (chebyshev1_filter.GetCoefficients()[0][0]+[0]*3)[:3], chebyshev1_filter.GetCoefficients()[0][1]
numeratorcb4, denominatorcb4 = (chebyshev1_filter.GetCoefficients()[0][0]+[0]*3)[:3], chebyshev1_filter.GetCoefficients()[0][1]
numeratorcb5, denominatorcb5 = (chebyshev1_filter.GetCoefficients()[0][0]+[0]*3)[:3], chebyshev1_filter.GetCoefficients()[0][1]
threshold_decay = [inital_threshold_decay]
threshold_assymetry = [initial_threshold_assymetry]

# Optimize the parameters by reducing the error function
result = scipy.optimize.minimize(errorfunction,
                                (threshold_decay+threshold_assymetry
                                 +numeratorbw1+denominatorbw1+numeratorbw2+denominatorbw2+numeratorbw3+denominatorbw3+numeratorbw4+denominatorbw4+numeratorbw5+denominatorbw5
                                 +numeratorcb1+denominatorcb1+numeratorcb2+denominatorcb2+numeratorcb3+denominatorcb3+numeratorcb4+denominatorcb4+numeratorcb5+denominatorcb5),
                                 method= method)


# print result and plot output
print result
merge_ipandop = sumpf.modules.MergeSpectrums(spectrums=[tf_measured.GetOutput(),tf_simulated.GetOutput()]).GetOutput()
merge_ipandop_harmonics = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_withharmonics.GetSpectrum(),tf_simulated_withharmonics.GetSpectrum()]).GetOutput()
merge_ipandop_fundamental = sumpf.modules.MergeSpectrums(spectrums=[tf_measured_fundamental.GetOutput(),tf_simulated_fundamental.GetOutput()]).GetOutput()
common.plot.log()
common.plot.plot(merge_ipandop)
common.plot.plot(merge_ipandop_fundamental)
common.plot.plot(merge_ipandop_harmonics)