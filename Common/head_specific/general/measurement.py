import sumpf

sampling_rate = 48000.0
start_frequency = 2.0
stop_frequency = 20000.0
fade_out = 0.02
silence_duration = 0.03

def get_samplingrate():
	return sampling_rate

def get_fade_length():
	return sumpf.modules.DurationToLength(duration=fade_out, samplingrate=get_samplingrate()).GetLength()

def get_silence_length():
	return sumpf.modules.DurationToLength(duration=silence_duration, samplingrate=get_samplingrate()).GetLength()

def get_sweep(length):
	# get lengths from durations
	d2l = sumpf.modules.DurationToLength(duration=fade_out, samplingrate=sampling_rate)
	fade_length = d2l.GetLength()
	d2l.SetDuration(silence_duration)
	silence_length = d2l.GetLength()
	sumpf.destroy_connectors(d2l)
	sweep_length = length - silence_length
	# get signals
	slg = sumpf.modules.SilenceGenerator(samplingrate=sampling_rate, length=silence_length)
	silence = slg.GetSignal()
	sumpf.destroy_connectors(slg)
	swg = sumpf.modules.SweepGenerator(start_frequency=start_frequency,
	                                   stop_frequency=stop_frequency,
	                                   function=sumpf.modules.SweepGenerator.Exponential,
	                                   interval=(0, -fade_length),
	                                   samplingrate=sampling_rate,
	                                   length=sweep_length)
	sweep = swg.GetSignal()
	sumpf.destroy_connectors(swg)
	wng = sumpf.modules.WindowGenerator(fall_interval=(-fade_length, -1),
	                                    function=sumpf.modules.WindowGenerator.Hanning(),
	                                    samplingrate=sampling_rate,
	                                    length=sweep_length)
	window = wng.GetSignal()
	sumpf.destroy_connectors(wng)
	# combine signals
	windowed_sweep = sweep * window
	cat = sumpf.modules.ConcatenateSignals(signal1=windowed_sweep, signal2=silence)
	concatenated_sweep = cat.GetOutput()
	sumpf.destroy_connectors(cat)
	return concatenated_sweep

def get_sweep_properties(sweep_signal):
	sweep_duration = sweep_signal.GetDuration() - fade_out - silence_duration
	return start_frequency, stop_frequency, sweep_duration
