def get_octaveband_frequencies():
	return (15.625, 31.25, 62.5, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0)

def get_measured_octaveband_frequencies():
	return (31.2, 62.5, 127.0, 251.0, 499.0, 1009.0, 2011.0, 4019.0, 8009.0, 16033.0)

def get_resonance_frequency(speaker_name):
	speaker_resonance_frequencies = {"Visaton BF45": 194.0, "Sonavox Low": 41.0, "Sonavox Mid": 42.0, "Sonavox High": 1330.0, "Commander Keen": 369.0}
	return speaker_resonance_frequencies[speaker_name]

def get_measured_speaker_frequencies(speaker_name):
	measured_frequencies = {"Visaton BF45": [199.0 * f for f in [0.125, 0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0]],
	                        "Sonavox Low": [47.0 * f for f in [0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0, 250.0]],
	                        "Sonavox Mid": [47.0 * f for f in [0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0, 250.0]],
	                        "Sonavox High": [1550.0 * f for f in [0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0]],
	                        "Commander Keen": [31.2, 62.5, 127.0, 251.0, 499.0, 1009.0, 2011.0, 4019.0, 8009.0, 16033.0]}
	return measured_frequencies[speaker_name]

def find_nearest_measured_frequency(frequency):
	f_new = 31.2
	for speaker_name in ["Visaton BF45", "Sonavox Low", "Sonavox High", "Commander Keen"]:
		for f_test in get_measured_speaker_frequencies(speaker_name):
			if abs(frequency - f_test) < abs(frequency - f_new):
				f_new = f_test
	return f_new
