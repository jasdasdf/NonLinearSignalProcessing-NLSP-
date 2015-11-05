import sumpf

class Spectrogram(object):
	def __init__(self, spectrums, samplingrate):
		self.__spectrums = spectrums
		self.__samplingrate = samplingrate

	def GetSpectrums(self):
		return self.__spectrums

	def GetSamplingRate(self):
		return self.__samplingrate

	def __len__(self):
		return len(self.__spectrums)



def get_spectrogram(signal, window, overlap):
	if isinstance(overlap, float):
		overlap = int(round(overlap * len(window)))
	zeros = sumpf.modules.SilenceGenerator(samplingrate=signal.GetSamplingRate(), length=overlap).GetSignal()
	padded = sumpf.modules.ConcatenateSignals(signal1=zeros, signal2=signal).GetOutput()
	padded = sumpf.modules.ConcatenateSignals(signal1=padded, signal2=zeros).GetOutput()
	spectrums = []
	for b in range(len(window), len(padded), len(window) - overlap):
		cut = sumpf.modules.CutSignal(signal=padded, start=b - len(window), stop=b).GetOutput()
		windowed = cut * window
		fftd = sumpf.modules.FourierTransform(signal=windowed).GetSpectrum()
		zerophase = sumpf.Spectrum(channels=fftd.GetMagnitude(), resolution=fftd.GetResolution())
		spectrums.append(zerophase)
	return Spectrogram(spectrums=spectrums, samplingrate=len(spectrums) / signal.GetDuration())

