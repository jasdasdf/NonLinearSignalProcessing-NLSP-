import math
import sumpf

output_path = "D:/Daten/Anregungssignale/"

sampling_rate = head_specific.get_samplingrate()

# frequencies for narrow band signals
frequency_banks = [(31.2, 62.5, 127.0, 251.0, 499.0, 1009.0, 2011.0, 4019.0, 8009.0, 16033.0),
                   tuple([199.0 * f for f in [0.125, 0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0]]), 			# Visaton BF 45
                   tuple([47.0 * f for f in [0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0, 250.0]]), 			# Sonavox Tieftoener
#                   tuple([52.0 * f for f in [0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0, 250.0]]), 			# Sonavox Mitteltoener (Wassertest)
                   tuple([1550.0 * f for f in [0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0]])]	# Sonavox Hochtoener

# noise signal parameters
seed = 1623
standard_deviation = 0.225

# derived values
fade_length = sumpf.modules.DurationToLength(duration=fade_out, samplingrate=sampling_rate).GetLength()
silence_length = sumpf.modules.DurationToLength(duration=silence_duration, samplingrate=sampling_rate).GetLength()
silence = sumpf.modules.SilenceGenerator(samplingrate=sampling_rate, length=silence_length).GetSignal()

# speech
speeches = ["D:/Daten/Andere/Freiburger Sprachtest/intro_zusammengefasst.wav",
            "D:/Daten/Andere/Freiburger Sprachtest/woerter01.wav",
            "D:/Daten/Andere/HEAD-Hoerversuch/sprecher_weiblich.wav"]
for i, f in enumerate(speeches):
	speech = sumpf.modules.SignalFile(filename=f).GetSignal()
	speech = sumpf.modules.SplitSignal(data=speech, channels=[0]).GetOutput()
	if speech.GetSamplingRate() != sampling_rate:
		speech = sumpf.modules.ResampleSignal(signal=speech, samplingrate=sampling_rate, algorithm=sumpf.modules.ResampleSignal.SINC).GetOutput()
	if len(speech) % 2 != 0:
		speech = speech[0:-1]
	sumpf.modules.SignalFile(filename=output_path + "Speech %i" % (i + 1), signal=speech, format=sumpf.modules.SignalFile.WAV_FLOAT)

# music
songs = ["D:/Daten/Gemessen/Messungen Diplomarbeit/Excitation/music.npz"]
for i, f in enumerate(songs):
	music = sumpf.modules.SignalFile(filename=f, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
	music = sumpf.modules.SplitSignal(data=music, channels=[0]).GetOutput()
	if music.GetSamplingRate() != sampling_rate:
		music = sumpf.modules.ResampleSignal(signal=music, samplingrate=sampling_rate, algorithm=sumpf.modules.ResampleSignal.SINC).GetOutput()
	if len(music) % 2 != 0:
		speech = music[0:-1]
	sumpf.modules.SignalFile(filename=output_path + "Music %i" % (i + 1), signal=music, format=sumpf.modules.SignalFile.WAV_FLOAT)
exit()

# sweeps
for degree in [14, 16, 18, 19, 20]:
	signal_length = 2 ** degree
	sweep = head_specific.get_sweep(signal_length)
	sumpf.modules.SignalFile(filename=output_path + "Sweep %i" % degree, signal=sweep, format=sumpf.modules.SignalFile.WAV_FLOAT)

# seeds:
# 2**18: 0, 2**19: 0, 2**20:173, 120s:

# noises
for degree in [18, 19, 20]:
	signal_length = 2 ** degree
	excitation_length = signal_length - silence_length
	clipped = True
	noise = None
	noisegenerator = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0, standard_deviation=standard_deviation),
	                                              samplingrate=sampling_rate,
	                                              length=excitation_length)
	while clipped:
		if seed % 100 == 0:
			print "Trying", seed, "(%i)" % degree
		noisegenerator.Seed(seed)
		noise = noisegenerator.GetSignal()
		if min(noise.GetChannels()[0]) > -1.0 and max(noise.GetChannels()[0]) < 1.0:
			print "Seed for degree", degree, "is", seed, "(%f, %f)" % (min(noise.GetChannels()[0]), max(noise.GetChannels()[0]))
			clipped = False
		else:
			seed += 1
	concatenated_noise = sumpf.modules.ConcatenateSignals(signal1=noise, signal2=silence).GetOutput()
	sumpf.modules.SignalFile(filename=output_path + "Noise %i" % degree, signal=concatenated_noise, format=sumpf.modules.SignalFile.WAV_FLOAT)

# sines
for frequencies in frequency_banks:
	for frequency in frequencies:
		# sine
		sine_length = 2 ** 19
		sine = sumpf.modules.SineWaveGenerator(frequency=frequency, samplingrate=sampling_rate, length=sine_length).GetSignal()
		window = sumpf.modules.WindowGenerator(raise_interval=(0, fade_length),
		                                       fall_interval=(-fade_length, -1),
		                                       function=sumpf.modules.WindowGenerator.Hanning(),
		                                       samplingrate=sampling_rate,
		                                       length=sine_length).GetSignal()
		windowed_sine = sine * window
		sumpf.modules.SignalFile(filename=output_path + "Sine %.1fHz" % frequency, signal=windowed_sine, format=sumpf.modules.SignalFile.WAV_FLOAT)

# narrow band noises
for frequencies in frequency_banks:
	properties = sumpf.modules.ChannelDataProperties(signal_length=2 ** 19, samplingrate=sampling_rate)
	corner_frequencies = [(frequencies[i] - frequencies[i - 1]) / (math.log(frequencies[i] / frequencies[i - 1])) for i in range(1, len(frequencies))]
	filters = []
	filterh = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH_LOWPASS(frequency=corner_frequencies[0], order=4), resolution=properties.GetResolution(), length=properties.GetSpectrumLength()).GetSpectrum()
	filterlh = filterh * filterh
	relabeled = sumpf.modules.RelabelSpectrum(input=filterlh, labels=["0Hz-%.1fHz" % corner_frequencies[0]]).GetOutput()
	filters.append(relabeled)
	for i in range(1, len(corner_frequencies)):
		filterl = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH_HIGHPASS(frequency=corner_frequencies[i - 1], order=4), resolution=properties.GetResolution(), length=properties.GetSpectrumLength()).GetSpectrum()
		filterh = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH_LOWPASS(frequency=corner_frequencies[i], order=4), resolution=properties.GetResolution(), length=properties.GetSpectrumLength()).GetSpectrum()
		filterlh = filterl * filterl * filterh * filterh
		relabeled = sumpf.modules.RelabelSpectrum(input=filterlh, labels=["%.1fHz-%.1fHz" % (corner_frequencies[i - 1], corner_frequencies[i])]).GetOutput()
		filters.append(relabeled)
	filterl = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH_HIGHPASS(frequency=corner_frequencies[-1], order=4), resolution=properties.GetResolution(), length=properties.GetSpectrumLength()).GetSpectrum()
	filterlh = filterl * filterl
	relabeled = sumpf.modules.RelabelSpectrum(input=filterlh, labels=["%.1fHz-%.1fHz" % (corner_frequencies[-1], sampling_rate // 2)]).GetOutput()
	filters.append(relabeled)
	for i in range(len(filters)):
		excitation_length = properties.GetSignalLength() - silence_length
		clipped = True
		noise = None
		noisegenerator = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0, standard_deviation=standard_deviation * (len(filters) - i)),
		                                              samplingrate=sampling_rate,
		                                              length=excitation_length)
		filtered_noise = None
		while clipped:
			if seed % 100 == 0:
				print "Trying", seed, "(%s)" % filters[i].GetLabels()[0]
			noisegenerator.Seed(seed)
			noise = noisegenerator.GetSignal()
			concatenated_noise = sumpf.modules.ConcatenateSignals(signal1=noise, signal2=silence).GetOutput()
			noise_spectrum = sumpf.modules.FourierTransform(signal=concatenated_noise).GetSpectrum()
			filtered_spectrum = noise_spectrum * filters[i]
			filtered_noise = sumpf.modules.InverseFourierTransform(spectrum=filtered_spectrum).GetSignal()
			if min(filtered_noise.GetChannels()[0]) > -1.0 and max(filtered_noise.GetChannels()[0]) < 1.0:
				print "Seed for filter", filters[i].GetLabels()[0], "is", seed, "(%f, %f)" % (min(filtered_noise.GetChannels()[0]), max(filtered_noise.GetChannels()[0]))
				clipped = False
			else:
				seed += 1
		sumpf.modules.SignalFile(filename=output_path + "Narrowband Noise %s" % filters[i].GetLabels()[0], signal=filtered_noise, format=sumpf.modules.SignalFile.WAV_FLOAT)

# narrow band sweeps
for frequencies in frequency_banks:
	signal_length = 2 ** 19
	excitation_length = signal_length - silence_length
	corner_frequencies = [(frequencies[i] - frequencies[i - 1]) / (math.log(frequencies[i] / frequencies[i - 1])) for i in range(1, len(frequencies))]
	intervals = [[start_frequency, corner_frequencies[0]]]
	for i in range(1, len(corner_frequencies)):
		intervals.append([corner_frequencies[i - 1], corner_frequencies[i]])
	intervals.append([corner_frequencies[-1], stop_frequency])
	window = sumpf.modules.WindowGenerator(fall_interval=(-fade_length, -1),
	                                       function=sumpf.modules.WindowGenerator.Hanning(),
	                                       samplingrate=sampling_rate,
	                                       length=excitation_length).GetSignal()
	for interval in intervals:
		sweep = sumpf.modules.SweepGenerator(start_frequency=interval[0],
		                                     stop_frequency=interval[1],
		                                     function=sumpf.modules.SweepGenerator.Exponential,
		                                     interval=(0, -fade_length),
		                                     samplingrate=sampling_rate,
		                                     length=excitation_length).GetSignal()
		windowed_sweep = sweep * window
		concatenated_sweep = sumpf.modules.ConcatenateSignals(signal1=windowed_sweep, signal2=silence).GetOutput()
		sumpf.modules.SignalFile(filename=output_path + "Narrowband Sweep %.1fHz-%.1fHz" % tuple(interval), signal=concatenated_sweep, format=sumpf.modules.SignalFile.WAV_FLOAT)

# a fancy sweep composition
start_frequency = 2.0
stop_frequency = 20000.0
silence_duration = 0.03
fade_out = 0.02
signal_length = 2 ** 18
fade_length = sumpf.modules.DurationToLength(duration=fade_out, samplingrate=sampling_rate).GetLength()
window = sumpf.modules.WindowGenerator(raise_interval=(0, fade_length),
                                       fall_interval=(-fade_length, -1),
                                       function=sumpf.modules.WindowGenerator.Hanning(),
                                       samplingrate=sampling_rate,
                                       length=signal_length).GetSignal()
raising_sweep1 = sumpf.modules.SweepGenerator(start_frequency=start_frequency,
                                              stop_frequency=stop_frequency / math.e,
                                              function=sumpf.modules.SweepGenerator.Exponential,
                                              interval=(fade_length, -fade_length),
                                              samplingrate=sampling_rate,
                                              length=signal_length).GetSignal()
raising_sweep2 = sumpf.modules.SweepGenerator(start_frequency=start_frequency * 2.0 ** 0.5,
                                              stop_frequency=stop_frequency / 2.0 ** 0.5,
                                              function=sumpf.modules.SweepGenerator.Exponential,
                                              interval=(fade_length, -fade_length),
                                              samplingrate=sampling_rate,
                                              length=signal_length).GetSignal()
raising_sweep3 = sumpf.modules.SweepGenerator(start_frequency=start_frequency * math.e,
                                              stop_frequency=stop_frequency,
                                              function=sumpf.modules.SweepGenerator.Exponential,
                                              interval=(fade_length, -fade_length),
                                              samplingrate=sampling_rate,
                                              length=signal_length).GetSignal()
falling_sweep1 = sumpf.modules.SweepGenerator(start_frequency=stop_frequency / math.e,
                                              stop_frequency=start_frequency,
                                              function=sumpf.modules.SweepGenerator.Exponential,
                                              interval=(fade_length, -fade_length),
                                              samplingrate=sampling_rate,
                                              length=signal_length).GetSignal()
falling_sweep2 = sumpf.modules.SweepGenerator(start_frequency=stop_frequency / 2.0 ** 0.5,
                                              stop_frequency=start_frequency * 2.0 ** 0.5,
                                              function=sumpf.modules.SweepGenerator.Exponential,
                                              interval=(fade_length, -fade_length),
                                              samplingrate=sampling_rate,
                                              length=signal_length).GetSignal()
falling_sweep3 = sumpf.modules.SweepGenerator(start_frequency=stop_frequency,
                                              stop_frequency=start_frequency * math.e,
                                              function=sumpf.modules.SweepGenerator.Exponential,
                                              interval=(fade_length, -fade_length),
                                              samplingrate=sampling_rate,
                                              length=signal_length).GetSignal()
signals = [raising_sweep1 * window,
           falling_sweep1 * window,
           sumpf.modules.NormalizeSignal(input=(raising_sweep1 + raising_sweep2) * window).GetOutput(),
           sumpf.modules.NormalizeSignal(input=(falling_sweep1 + falling_sweep2) * window).GetOutput(),
           sumpf.modules.NormalizeSignal(input=(raising_sweep1 + raising_sweep2 + raising_sweep3) * window).GetOutput(),
           sumpf.modules.NormalizeSignal(input=(falling_sweep1 + falling_sweep2 + falling_sweep3) * window).GetOutput(),
           sumpf.modules.NormalizeSignal(input=(raising_sweep1 + falling_sweep3) * window).GetOutput(),
           sumpf.modules.NormalizeSignal(input=(raising_sweep3 + falling_sweep1) * window).GetOutput()]
signal = signals[0]
for i in range(1, len(signals)):
	signal = sumpf.modules.ConcatenateSignals(signal1=signal, signal2=signals[i]).GetOutput()
sumpf.modules.SignalFile(filename=output_path + "Sweeps", signal=signal, format=sumpf.modules.SignalFile.WAV_FLOAT)
