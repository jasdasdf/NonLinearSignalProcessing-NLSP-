import sys
sys.path.append("C:\\Users\jonas.schulte-coerne\\workspace\\Privat\\SuMPF\\source")

import math
import os
import win32com.client
import sumpf

#try:
#    LicenseHelper = win32com.client.Dispatch('LicenseHelperLib.LicenseHelper')
#    LicenseHelper.AddProduct(6800, 82) # ACQUA Basics
#    LicenseHelper.AddProduct(6810, 80) # ACQUA Full-License
#    LicenseHelper.LoginProducts()
#    import atexit
#    atexit.register(LicenseHelper.ReleaseAndClearAllProducts, True)
#except win32com.client.pywintypes.com_error:
#    pass
#
#
#class HdfData(object):
#	def __init__(self, abscissas, channels):
#		self.__abscissas = abscissas
#		self.__channels = channels
#	def GetAbscissas(self):
#		return self.__abscissas
#	def GetChannels(self):
#		return self.__channels
#
#
#
#class Abscissa(object):
#	"""
#	Abscissas behave a bit like a tuple:
#	 - you can access a scan value via 'abscissa_object[index]'
#	 - you can get the number of scans via 'len(abscissa_object)'
#	 - you can loop over the scans via 'for scan in abscissa_object:'
#	The metadata can be accessed via getter methods, e.g. 'abscissa_object.GetName()'.
#	"""
#	def __init__(self, name, unit, quantity, tags):
#		self.__name = name
#		self.__unit = unit
#		self.__quantity = quantity
#		self.__tags = tags
#	def GetName(self):
#		return self.__name
#	def GetUnit(self):
#		return self.__unit
#	def GetQuantity(self):
#		return self.__quantity
#	def GetTags(self):
#		return self.__tags
#	def __getitem__(self, index):
#		raise NotImplementedError("How dare you instantiating an abstract class!?")
#	def __len__(self):
#		raise NotImplementedError("How dare you instantiating an abstract class!?")
#
#
#
#class EquidistantValuesAbscissa(Abscissa):
#	"""
#	Abscissas behave a bit like a tuple:
#	 - you can access a scan value via 'abscissa_object[index]'
#	 - you can get the number of scans via 'len(abscissa_object)'
#	 - you can loop over the scans via 'for scan in abscissa_object:'
#	The metadata can be accessed via getter methods, e.g. 'abscissa_object.GetName()'.
#	"""
#	def __init__(self, delta, length, name, unit, quantity, tags):
#		Abscissa.__init__(self, name=name, unit=unit, quantity=quantity, tags=tags)
#		self.__delta = delta
#		self.__length = length
#	def GetDelta(self):
#		return self.__delta
#	def __getitem__(self, index):
#		if index < self.__length:
#			return index * self.__delta
#		else:
#			raise IndexError("list index out of range")
#	def __len__(self):
#		return self.__length
#
#
#
#class ExplicitValuesAbscissa(Abscissa):
#	"""
#	Abscissas behave a bit like a tuple:
#	 - you can access a scan value via 'abscissa_object[index]'
#	 - you can get the number of scans via 'len(abscissa_object)'
#	 - you can loop over the scans via 'for scan in abscissa_object:'
#	The metadata can be accessed via getter methods, e.g. 'abscissa_object.GetName()'.
#	"""
#	def __init__(self, scans, name, unit, quantity, tags):
#		Abscissa.__init__(self, name=name, unit=unit, quantity=quantity, tags=tags)
#		self.__scans = scans
#	def __getitem__(self, index):
#		return self.__scans[index]
#	def __len__(self):
#		return len(self.__scans)
#
#
## Flags for the error handling of the read_hdf function
#RAISE_ERROR = 1
#PRINT_MESSAGE = 2
#SKIP = 3
#abscissa = None
#def read_hdf(filename, on_error=RAISE_ERROR):
#	if not os.path.exists(filename):
#		raise RuntimeError("Could not find HDF: %s" % filename)
#	comserver = win32com.client.gencache.EnsureDispatch('HEADDataset.DatasetFactory.1')
#	dataset = comserver.Open(filename)[0]
#	# parse the absissas into a list of objects
#	abscissas = []
#	for a in range(1, dataset.Abscissas.Count + 1):
#		abscissa = dataset.Abscissas.Item(a)
#		kind = abscissa.Kind
#		name = abscissa.Name
#		unit = abscissa.Unit
#		quantity = abscissa.Quantity
#		tags = abscissa.Tags
#		length = abscissa.NbrOfScans
#		if kind == 1:
#			delta = abscissa.DeltaValue
#			object = EquidistantValuesAbscissa(delta=delta, length=length, name=name, unit=unit, quantity=quantity, tags=tags)
#			abscissas.append(object)
#		elif kind == 2:
#			scans = [0.0] * length
#			trash, scans = abscissa.Read(scans)
#			object = ExplicitValuesAbscissa(scans=scans, name=name, unit=unit, quantity=quantity, tags=tags)
#			abscissas.append(object)
#		elif on_error == RAISE_ERROR:
#			raise NotImplementedError("The kind %i of abscissa %i is not (yet) supported" % (kind, a))
#		elif on_error == PRINT_MESSAGE:
#			print("The kind %i of abscissa %i is not (yet) supported" % (kind, a))
#	# parse the channels into a list of channels, which themselves are a list of samples
#	if len(abscissas) > 0:
#		channels = []
#		for c in range(1, dataset.Channels.Count + 1):
#			channel = dataset.Channels.Item(c)
#			samples = 0.0
#			for a in range(len(abscissas) - 1, -1, -1):
#				new_samples = []
#				for i in range(len(abscissas[a])):
#					new_samples.append(samples)
#				samples = new_samples
#			trash, samples = channel.Read(samples)
#			channels.append(tuple(samples))
#		return HdfData(abscissas=tuple(abscissas), channels=tuple(channels))
#	else:
#		return HdfData(abscissas=(), channels=())

#                name            messung   korrektur kanal1   korrektur kanal2
measurements = [("Sonavox Low", "Current1", 1.0, 10.0 ** (16.0 / 20.0)),
                ("Sonavox Mid", "Current1", 10.0 ** (-6.0 / 20.0), 10.0 ** (10.0 / 20.0)),
                ("Visaton BF45", "Current1", 1.0, 10.0 ** (10.0 / 20.0)),
                ("Sonavox High", "Current1", 1.0, 10.0 ** (10.0 / 20.0)),
                ("Sonavox Low", "Sound Pressure", 10.0 ** (-6.0 / 20.0), 1.0),
                ("Sonavox Mid", "Sound Pressure", 10.0 ** (-6.0 / 20.0), 1.0),
                ("Sonavox High", "Sound Pressure", 10.0 ** (-6.0 / 20.0), 1.0),
                ("Visaton BF45", "Sound Pressure", 10.0 ** (-6.0 / 20.0), 1.0),
                ("Visaton BF45", "Current2", 10.0 ** (-6.0 / 20.0), 10 ** (8 / 20)),
                ("Sonavox High", "Current2", 10.0 ** (-6.0 / 20.0), 10 ** (8 / 20)),
                ("Sonavox Mid", "Current2", 10.0 ** (-6.0 / 20.0), 10 ** (8 / 20)),
                ("Sonavox Low", "Current2", 10.0 ** (-6.0 / 20.0), 10 ** (8 / 20))]

frequency_banks = [(31.2, 62.5, 127.0, 251.0, 499.0, 1009.0, 2011.0, 4019.0, 8009.0, 16033.0),
                   tuple([199.0 * f for f in [0.125, 0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0]]), 			# Visaton BF 45
                   tuple([47.0 * f for f in [0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0, 250.0]]), 			# Sonavox Tieftoener
#                   tuple([52.0 * f for f in [0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0, 20.0, 50.0, 250.0]]), 			# Sonavox Mitteltoener (Wassertest)
                   tuple([1550.0 * f for f in [0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0 / 1.3, 1.0, 1.5, 2.0, 4.0, 9.0]])]	# Sonavox Hochtoener
i = 2
smds = {}
for d in (14, 16, 18, 19, 20):
	smds[i] = "Sweep %i" % d
	i += 1
for d in (18, 19, 20):
	smds[i] = "Noise %i" % d
	i += 1
for n in ("Speech 1", "Speech 2", "Speech 3", "Music", "Sweeps"):
	smds[i] = n
	i += 1
for b in frequency_banks:
	for f in b:
		smds[i] = "Sine %.1fHz" % f
		i += 1
for b in frequency_banks:
	corner_frequencies = [2.0] + [(b[k] - b[k - 1]) / (math.log(b[k] / b[k - 1])) for k in range(1, len(b))] + [20000.0]
	for f in range(1, len(corner_frequencies)):
		smds[i] = "Narrowband Sweep %.1fHz-%.1fHz" % (corner_frequencies[f - 1], corner_frequencies[f])
		i += 1
for b in frequency_banks:
	corner_frequencies = [0.0] + [(b[k] - b[k - 1]) / (math.log(b[k] / b[k - 1])) for k in range(1, len(b))] + [24000.0]
	for f in range(1, len(corner_frequencies)):
		smds[i] = "Narrowband Noise %.1fHz-%.1fHz" % (corner_frequencies[f - 1], corner_frequencies[f])
		i += 1

for k in smds:
	for i, m in enumerate(measurements):
		name, measurement, correction1, correction2 = m
		output_dir = "C:/Users/jonas.schulte-coerne/workspace/Daten/" + name + "/" + measurement
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		hdf = read_hdf("C:/Users/jonas.schulte-coerne/workspace/Daten/ACQUA/Lautsprechermessungen/Exportiert/Touran Lautsprecher/Lautsprechermessungen_SMD%i_Index%i_TimeSignal.dat" % (k, i))
		signal = sumpf.Signal(channels=hdf.GetChannels(), samplingrate=48000.0, labels=("Voltage", measurement))
		corrected = sumpf.modules.AmplifySignal(input=signal, factor=[correction1, correction2])
		sumpf.modules.SignalFile(filename=output_dir + "/" + smds[k],
								 signal=corrected,
								 format=sumpf.modules.SignalFile.NUMPY_NPZ)
		sumpf.collect_garbage()
exit()

for e in excitations:
    for i in range(len(measurements)):
        for j in range(1, len(channel2)):
            index = i + 1#1 + i * len(channel2) + j
            hdf = read_hdf("C:/Users/jonas.schulte-coerne/workspace/Daten/ACQUA/Lautsprechermessungen/Exportiert/Abstandsmessungen/Lautsprechermessungen_SMD%i_Index%i_TimeSignal.dat" % (e, index))
            channels = hdf.GetChannels()
            samplingrate = 48000.0
            labels = (channel1, channel2[j])
            signal = sumpf.Signal(channels=channels, samplingrate=samplingrate, labels=labels)
            sumpf.modules.SignalFile(filename="C:/Users/jonas.schulte-coerne/workspace/Daten/Abstandsmessungen/%s - %s" % (excitations[e], measurements[i]),
                                     signal=signal,
                                     format=sumpf.modules.SignalFile.NUMPY_NPZ)
            sumpf.collect_garbage()
