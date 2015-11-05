import math
import os
import sumpf
import common
import head_specific
from classes import Copy, Filter
from filters import FilterSetup

def get_output_path(speaker_name, measurement_name, identification_name, mode, filterbank_type, filterbank_order):
	base_path = "D:/"
	if os.name == "posix":
		base_path = "/home/jonas/Desktop/Home/Dokumente/Arbeit/"
	modestring = "Continuous"
	if mode == FilterSetup.DISCRETE:
		modestring = "Discrete"
	return base_path + "Daten/Synthetisiert/Filterbank/%s - %s/%s - %s/%s - %i/" % (measurement_name, modestring, speaker_name, identification_name, filterbank_type, filterbank_order)

def measurement_data_exists(speaker_name, measurement_name, identification_name):
	data_path = head_specific.get_data_path(speaker_name, measurement_name)
	frequencies, corner_frequencies = get_speaker_frequencies(speaker_name, identification_name)[0:2]
	if identification_name in ["Sine", "Octave Sine"]:
		if not os.path.exists(data_path + "Sine %.1fHz.npz" % frequencies[0]):
			return False
	elif identification_name.startswith("Sweep") or identification_name.startswith("Noise"):
		if not os.path.exists(data_path + "%s.npz" % identification_name):
			return False
	elif identification_name.startswith("Octave Sweep"):
		if not os.path.exists(data_path + "Narrowband Sweep %.1fHz-%.1fHz.npz" % (corner_frequencies[0], corner_frequencies[1])):
			return False
	elif identification_name.startswith("Octave Noise"):
		if not os.path.exists(data_path + "Narrowband Noise %.1fHz-%.1fHz.npz" % (corner_frequencies[0], corner_frequencies[1])):
			return False
	else:
		if not os.path.exists(data_path + "%s %.1fHz-%.1fHz.npz" % (identification_name, corner_frequencies[0], corner_frequencies[1])):
			return False
	return True

def get_speaker_frequencies(speaker_name, identification_name, nth_octave=1.0):
	"""
	Returns a list of frequencies and a list of corner frequencies that can be
	used to find a file with measurement data.
	"""
	if identification_name.startswith("Sweep") or identification_name.startswith("Noise") or identification_name == "Sine":
		resonance_frequency = head_specific.get_resonance_frequency(speaker_name)
		x = -1.0
		while resonance_frequency * 2.0 ** (x / nth_octave) > 20.0:
			x -= 1.0
		highpass_frequency = resonance_frequency * 2.0 ** (x / nth_octave)
		frequencies = []
		x += 1.0
		f = resonance_frequency * 2.0 ** (x / nth_octave)
		while f < 20000.0:
			frequencies.append(f)
			x += 1.0
			f = resonance_frequency * 2.0 ** (x / nth_octave)
		lowpass_frequency = f
		if identification_name == "Sine":
			for i, f in enumerate(frequencies):
				frequencies[i] = head_specific.find_nearest_measured_frequency(f)
		corner_frequencies = common.get_corner_frequencies([highpass_frequency] + frequencies + [lowpass_frequency])
		return frequencies, corner_frequencies, highpass_frequency, lowpass_frequency
	else:
		frequencies = head_specific.get_measured_speaker_frequencies(speaker_name)
		if identification_name.startswith("Octave "):
			frequencies = head_specific.get_measured_octaveband_frequencies()
		corner_frequencies = common.get_corner_frequencies(frequencies)
		highpass_frequency = 10.0
		lowpass_frequency = 20000.0
		if "Sweep" in identification_name:
			corner_frequencies = [2.0] + corner_frequencies + [20000.0]
		else:
			corner_frequencies = [0.0] + corner_frequencies + [24000.0]
		return frequencies, corner_frequencies, highpass_frequency, lowpass_frequency

def get_narrowband_signals(speaker_name, measurement_name, identification_name, frequencies, corner_frequencies, filtersetup):
	"""
	Returns two lists of narrow band excitations and responses, that can be used
	to determine the nonlinear functions for the frequency bands
	"""
	data_path = head_specific.get_data_path(speaker_name, measurement_name)
	narrowband_excitations = {}
	narrowband_responses = {}
	if identification_name in ["Sine", "Octave Sine"]:
		for f in frequencies:
			narrowband = sumpf.modules.SignalFile(filename=data_path + "Sine %.1fHz" % f, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
			narrowband_excitations[f] = sumpf.modules.SplitSignal(data=narrowband, channels=[0]).GetOutput()
			narrowband_responses[f] = sumpf.modules.SplitSignal(data=narrowband, channels=[1]).GetOutput()
	elif identification_name.startswith("Noise") or identification_name == "Sweeps":
		signal = sumpf.modules.SignalFile(filename=data_path + "%s" % identification_name, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
		wideband_copy = Copy(signal=signal, frequencies=frequencies)
		wideband_filter = Filter()
		sumpf.connect(wideband_copy.GetOutput, wideband_filter.SetInput)
		sumpf.connect(filtersetup.GetFilters, wideband_filter.SetFilters)
		filtered = wideband_filter.GetOutput()
		for f in filtered:
			narrowband_excitations[f] = sumpf.modules.SplitSignal(data=filtered[f], channels=[0]).GetOutput()
			narrowband_responses[f] = sumpf.modules.SplitSignal(data=filtered[f], channels=[1]).GetOutput()
	elif identification_name.startswith("Sweep "):
		signal = sumpf.modules.SignalFile(filename=data_path + "%s" % identification_name, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
		excitation = sumpf.modules.SplitSignal(data=signal, channels=[0]).GetOutput()
		response = sumpf.modules.SplitSignal(data=signal, channels=[1]).GetOutput()
		sweep_start_frequency = 2.0
		sweep_stop_frequency = 20000.0
		silence_duration = 0.03
		fade_out = 0.02
		sweep_duration = signal.GetDuration() - (fade_out + silence_duration)
		sweep_fade_length = sumpf.modules.DurationToLength(duration=fade_out, samplingrate=signal.GetSamplingRate()).GetLength()
		sweep_silence_length = sumpf.modules.DurationToLength(duration=silence_duration, samplingrate=signal.GetSamplingRate()).GetLength()
		sweep_silence = sumpf.modules.SilenceGenerator(samplingrate=signal.GetSamplingRate(), length=sweep_silence_length).GetSignal()
		sweep_length = len(signal) - sweep_silence_length
		sweep_sweep = sumpf.modules.SweepGenerator(start_frequency=sweep_start_frequency,
		                                           stop_frequency=sweep_stop_frequency,
		                                           function=sumpf.modules.SweepGenerator.Exponential,
		                                           interval=(0, -sweep_fade_length),
		                                           samplingrate=signal.GetSamplingRate(),
		                                           length=sweep_length).GetSignal()
		sweep_window = sumpf.modules.WindowGenerator(fall_interval=(-sweep_fade_length, -1),
		                                             function=sumpf.modules.WindowGenerator.Hanning(),
		                                             samplingrate=signal.GetSamplingRate(),
		                                             length=sweep_length).GetSignal()
		sweep = sumpf.modules.ConcatenateSignals(signal1=sweep_sweep * sweep_window, signal2=sweep_silence).GetOutput()
		aligned_excitation_sweep = common.align_signals(sweep, excitation)[1]
		aligned_excitation_filled = common.append_zeros(aligned_excitation_sweep)
		aligned_excitation, aligned_response = common.align_signals(aligned_excitation_filled, response)
		k = (sweep_stop_frequency / sweep_start_frequency) ** (1.0 / sweep_duration)
		for i, f in enumerate(frequencies):
			start = int(round(math.log(corner_frequencies[i] / sweep_start_frequency, k) * signal.GetSamplingRate())) - (len(excitation) - len(aligned_excitation)) // 2
			stop = int(round(math.log(corner_frequencies[i + 1] / sweep_start_frequency, k) * signal.GetSamplingRate())) - (len(excitation) - len(aligned_excitation)) // 2
			if (start - stop) % 2 != 0:
				stop -= 1
			narrowband_excitations[f] = aligned_excitation[start:stop]
			narrowband_responses[f] = aligned_response[start:stop]
#			fade_length = (stop - start) // 100 - ((stop - start) // 100) % 2
#			window = sumpf.modules.WindowGenerator(raise_interval=(0, fade_length),
#			                                       fall_interval=(-fade_length, -1),
#			                                       function=sumpf.modules.WindowGenerator.Hanning(),
#			                                       samplingrate=signal.GetSamplingRate(),
#			                                       length=stop - start + fade_length).GetSignal()
#			narrowband_excitations[f] = aligned_excitation[start - fade_length // 2:stop + fade_length // 2] * window
#			narrowband_responses[f] = aligned_response[start - fade_length // 2:stop + fade_length // 2] * window
	elif identification_name.endswith("Sweep"):
		for i, f in enumerate(frequencies):
			narrowband = sumpf.modules.SignalFile(filename=data_path + "Narrowband Sweep %.1fHz-%.1fHz" % (corner_frequencies[i], corner_frequencies[i + 1]), format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
			narrowband_excitations[f] = sumpf.modules.SplitSignal(data=narrowband, channels=[0]).GetOutput()
			narrowband_responses[f] = sumpf.modules.SplitSignal(data=narrowband, channels=[1]).GetOutput()
	elif identification_name.endswith("Noise"):
		for i, f in enumerate(frequencies):
			narrowband = sumpf.modules.SignalFile(filename=data_path + "Narrowband Noise %.1fHz-%.1fHz" % (corner_frequencies[i], corner_frequencies[i + 1]), format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
			narrowband_excitations[f] = sumpf.modules.SplitSignal(data=narrowband, channels=[0]).GetOutput()
			narrowband_responses[f] = sumpf.modules.SplitSignal(data=narrowband, channels=[1]).GetOutput()
	sumpf.collect_garbage()
	return narrowband_excitations, narrowband_responses

