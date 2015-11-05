import os
import numpy
import sumpf
import head_specific
from determination import flags

def get_output_path(speaker_name, text, minimization_algorithms, iterations_per_step):
	base_path = "D:/"
	if os.name == "posix":
		base_path = "/home/jonas/Desktop/Home/Dokumente/Arbeit/"
	return base_path + "Daten/Synthetisiert/Auralisierung/%s/%s - %s %s/" % (speaker_name, text, str(minimization_algorithms).replace("[", "(").replace("]", ")"), str(iterations_per_step).replace("[", "(").replace("]", ")"),)

def load_measurement(speaker_name, measurement_name, excitation_name):
	filename = head_specific.get_data_path(speaker_name, measurement_name) + excitation_name
	# load file
	if not os.path.exists(filename + ".npz"):
		raise RuntimeError("The file %s.npz does not exist." % filename)
	signal = sumpf.modules.SignalFile(filename=filename, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
	if signal.IsEmpty():
		raise RuntimeError("The loaded signal from file %s is empty." % filename)
	# create short labels for the channels
	measurement_type = 0
	measurement_symbol = measurement_name
	if measurement_name.startswith("Excursion"):
		measurement_symbol = "x"
		measurement_type = flags.EXCURSION
	elif measurement_name.startswith("Velocity"):
		measurement_symbol = "v"
		measurement_type = flags.VELOCITY
	elif measurement_name.startswith("Acceleration"):
		measurement_symbol = "a"
		measurement_type = flags.ACCELERATION
	elif measurement_name.startswith("Current"):
		measurement_symbol = "i"
		measurement_type = flags.CURRENT
	elif measurement_name.startswith("Sound Pressure"):
		measurement_symbol = "p"
		measurement_type = flags.SOUND_PRESSURE
	else:
		raise ValueError("The measurement type could not be determined from the given measurement name \"%s\"" % measurement_name)
	excitation_shortname = excitation_name
	if excitation_name.startswith("Sweeps"):
		excitation_shortname = "sws" + "Sweeps".join(excitation_name.split("Sweeps")[1:]).strip()
	elif excitation_name.startswith("Speech"):
		excitation_shortname = "spx" + "Speech".join(excitation_name.split("Speech")[1:]).strip()
	elif excitation_name.startswith("Music"):
		excitation_shortname = "mus" + "Music".join(excitation_name.split("Music")[1:]).strip()
	elif excitation_name.startswith("Sweep"):
		excitation_shortname = "swp" + "Sweep".join(excitation_name.split("Sweep")[1:]).strip()
	elif excitation_name.startswith("Noise"):
		excitation_shortname = "noi" + "Noise".join(excitation_name.split("Noise")[1:]).strip()
	elif excitation_name.startswith("Sine"):
		excitation_shortname = "sin" + "Sine".join(excitation_name.split("Sine")[1:]).strip()
	elif excitation_name.startswith("Narrowband Sweep"):
		excitation_shortname = "nsw" + "Narrowband Sweep".join(excitation_name.split("Narrowband Sweep")[1:]).strip()
	elif excitation_name.startswith("Narrowband Noise"):
		excitation_shortname = "nns" + "Narrowband Noise".join(excitation_name.split("Narrowband Noise")[1:]).strip()
	label = "%s-%s" % (excitation_shortname, measurement_symbol)
	excitation = sumpf.modules.RelabelSignal(input=sumpf.modules.SplitSignal(data=signal, channels=[0]).GetOutput(), labels=[label]).GetOutput()
	response = sumpf.modules.RelabelSignal(input=sumpf.modules.SplitSignal(data=signal, channels=[1]).GetOutput(), labels=[label]).GetOutput()
	# sweep properties
	sweep_properties = None
	if excitation_shortname.startswith("swp"):
		sweep_properties = head_specific.get_sweep_properties(signal)
	# return
	if speaker_name == "Commander Keen" and measurement_name == "Current 1":
		response = response * 10.0 ** (10.0 / 20.0)	# compensate 10dB measurement error
	if speaker_name in ["Visaton BF45", "Sonavox Low", "Sonavox Mid"] and measurement_name == "Sound Pressure 1":
		response = response / 2.0	# compensate that these measurements have been made with the speaker and the microphone near the floor, which doubles the measured sound pressure
	normalize = False
	return excitation, response, measurement_type, normalize, sweep_properties

def get_side_information_filenames(output_path):
	max_number_length = 1
	filenames = []
	for filename in os.listdir(output_path):
		path = os.path.join(output_path, filename)
		if os.path.isfile(path):
			split = filename.split(" - ")
			if len(split) > 1:
				try:
					int(split[0])
				except ValueError:
					pass
				else:
					number_length = len(split[0])
					if number_length == max_number_length:
						filenames.append(path)
					elif number_length > max_number_length:
						max_number_length = number_length
						filenames = [path]
	return sorted(filenames)

def load_side_information(speaker_name, output_path, filename_list=None):
	filenames = filename_list
	if filenames is None:
		filenames = get_side_information_filenames(output_path)
	descriptions = []
	side_information = []
	for f in filenames:
		# get description
		filename = f.split(os.sep)[-1].split(os.altsep)[-1]
		no_number = " - ".join(filename.split(" - ")[1:])
		no_ending = ".npz".join(no_number.split(".npz")[0:-1])
		descriptions.append(no_ending)
		# get side information
		loaded = numpy.load(f)
		parameters = head_specific.auralization.get_parameters(speaker_name)
		parameters.UpdateCoefficientsFromDictionary(tuple(loaded["optimum_parameters"]))
		if loaded["parameter_set_type"] == flags.LINEAR:
			parameters = parameters.GetLinearized()
		elif loaded["parameter_set_type"] == flags.COMBINED:
			parameters = parameters.GetCombined()
		if loaded["parameter_mask"] is not None:
			parameters = parameters.GetMasked(loaded["parameter_mask"])
		information = [None] * 13
		information[flags.ITERATIONS] = loaded["iterations"]
		information[flags.EVALUATIONS] = loaded["evaluations"]
		information[flags.EVALUATIONS_PER_ITERATION] = tuple(loaded["evaluations_per_iteration"])
		information[flags.PARAMETERS] = parameters
		information[flags.PARAMETER_START_VALUES] = loaded["parameter_start_values"][()]
		information[flags.OPTIMUM_PARAMETERS] = tuple(loaded["optimum_parameters"])
		information[flags.COEFFICIENTS] = loaded["coefficients"]
		information[flags.ERRORS] = loaded["errors"]
		information[flags.EVALUATION_LABELS] = [tuple(l) for l in (loaded["evaluation_labels"])]
		information[flags.EVALUATION_TYPES] = list(loaded["evaluation_types"])
		information[flags.EVALUATION_FREQUENCIES] = [tuple(l) for l in (loaded["evaluation_frequencies"])]
		information[flags.EVALUATION_LINEARITIES] = list(loaded["evaluation_linearities"])
		information[flags.TIMES] = tuple(loaded["times"])
		side_information.append(information)
		loaded.close()
	return descriptions, side_information
