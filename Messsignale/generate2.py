import math
import sumpf
import head_specific

output_path = "D:/Daten/Anregungssignale/2 - "

base_frequency = 1000.0 + math.pi - math.e
nth_octave = 3.0
frequencies = []
for i in range(-18, 14):
	frequencies.append(base_frequency * 2.0 ** (i / nth_octave))

# noise signal parameters
seeds = {2 ** 18: 44, 2 ** 19: 241, 2 ** 20: 134, 120 * 48000: 151}
standard_deviation = 0.2

# derived values
sampling_rate = head_specific.get_samplingrate()
fade_length = head_specific.get_fade_length()
silence_length = head_specific.get_silence_length()
silence = sumpf.modules.SilenceGenerator(samplingrate=sampling_rate, length=silence_length).GetSignal()

# sweeps
for degree in [14, 16, 18, 19, 20]:
	signal_length = 2 ** degree
	sweep = head_specific.get_sweep(signal_length)
	sumpf.modules.SignalFile(filename=output_path + "Sweep %i" % degree, signal=sweep, format=sumpf.modules.SignalFile.WAV_FLOAT)

# noises
noisegenerator = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0, standard_deviation=standard_deviation),
                                              samplingrate=sampling_rate)
for signal_length in seeds:
	seed = seeds[signal_length]
	excitation_length = signal_length - silence_length
	degree = int(round(math.log(signal_length, 2)))
	clipped = True
	noisegenerator.SetLength(excitation_length)
	while clipped:
#		if seed % 100 == 0:
#			print "Trying", seed, "(%i)" % degree
		noisegenerator.Seed(seed)
		noise = noisegenerator.GetSignal()
		if min(noise.GetChannels()[0]) > -1.0 and max(noise.GetChannels()[0]) < 1.0:
#			print "Seed for degree", degree, "is", seed, "(%f, %f)" % (min(noise.GetChannels()[0]), max(noise.GetChannels()[0]))
			clipped = False
			concatenated_noise = sumpf.modules.ConcatenateSignals(signal1=noise, signal2=silence).GetOutput()
			filename = "Noise %i" % degree
			if 2 ** degree != signal_length:
				filename = "Noise %is" % int(round((signal_length / sampling_rate)))
			sumpf.modules.SignalFile(filename=output_path + filename, signal=concatenated_noise, format=sumpf.modules.SignalFile.WAV_FLOAT)
		else:
			seed += 1

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

# sines
sine_length = 2 ** 21
window = sumpf.modules.WindowGenerator(raise_interval=(0, fade_length),
                                       fall_interval=(-fade_length, -1),
                                       function=sumpf.modules.WindowGenerator.Hanning(),
                                       samplingrate=sampling_rate,
                                       length=sine_length).GetSignal()
generator = sumpf.modules.SineWaveGenerator(samplingrate=sampling_rate, length=sine_length)
for frequency in frequencies:
	generator.SetFrequency(frequency)
	sine = generator.GetSignal() * window
	sumpf.modules.SignalFile(filename=output_path + "Sine %.1fHz" % frequency, signal=sine, format=sumpf.modules.SignalFile.WAV_FLOAT)

# fancy sweep compositions
for degree in [18, 20, 21]:
	start_frequency = 2.0
	stop_frequency = 20000.0
	silence_duration = 0.03
	fade_out = 0.02
	signal_length = 2 ** (degree - 2)
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
	sumpf.modules.SignalFile(filename=output_path + "Sweeps %i" % degree, signal=signal, format=sumpf.modules.SignalFile.WAV_FLOAT)

