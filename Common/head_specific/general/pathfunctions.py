import os

def get_data_path(speaker_name, measurement_name):
	base_path = "D:/"
	if os.name == "posix":
		base_path = "/home/jonas/Desktop/Home/Dokumente/Arbeit/"
	return base_path + "Daten/Gemessen/%s/%s/" % (speaker_name, measurement_name)
