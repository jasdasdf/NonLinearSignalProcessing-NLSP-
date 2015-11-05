import math
import numpy
import sumpf

def get_transfer_function(excitation, response):
	fft = sumpf.modules.FourierTransform(signal=excitation)
	excitation_spectrum = fft.GetSpectrum()
	fft.SetSignal(response)
	response_spectrum = fft.GetSpectrum()
	sumpf.destroy_connectors(fft)
	rgi = sumpf.modules.RegularizedSpectrumInversion(spectrum=excitation_spectrum)
	regularized = rgi.GetOutput()
	sumpf.destroy_connectors(rgi)
	if len(regularized.GetChannels()) == 1 and  len(response_spectrum.GetChannels()) != 1:
		cpy = sumpf.modules.CopySpectrumChannels(input=regularized, channelcount=len(response_spectrum.GetChannels()))
		regularized = cpy.GetOutput()
		sumpf.destroy_connectors(cpy)
	cls = sumpf.modules.CopyLabelsToSpectrum(data_input=response_spectrum * regularized, label_input=response)
	relabeled = cls.GetOutput()
	sumpf.destroy_connectors(cls)
	return relabeled

def get_impulse_response(excitation, response):
	transferfunction = get_transfer_function(excitation, response)
	ifft = sumpf.modules.InverseFourierTransform(spectrum=transferfunction)
	result = ifft.GetSignal()
	sumpf.destroy_connectors(ifft)
	return result

def get_cleaned_impulse_response(excitation, response, window_start, window_stop):
	impulse_response = get_impulse_response(excitation, response)
	wg = sumpf.modules.WindowGenerator(fall_interval=[window_start, window_stop], samplingrate=impulse_response.GetSamplingRate(), length=window_stop)
	window = wg.GetSignal()
	sumpf.destroy_connectors(wg)
	if len(window.GetChannels()) == 1 and  len(impulse_response.GetChannels()) != 1:
		cpy = sumpf.modules.CopySignalChannels(input=window, channelcount=len(impulse_response.GetChannels()))
		window = cpy.GetOutput()
		sumpf.destroy_connectors(cpy)
	cls = sumpf.modules.CopyLabelsToSignal(data_input=impulse_response[0:window_stop] * window, label_input=response)
	relabeled = cls.GetOutput()
	sumpf.destroy_connectors(cls)
	return relabeled

def get_cleaned_transfer_function(excitation, response, window_start, window_stop):
	impulse_response = get_cleaned_impulse_response(excitation, response, window_start, window_stop)
	fft = sumpf.modules.FourierTransform(signal=impulse_response)
	result = fft.GetSpectrum()
	sumpf.destroy_connectors(fft)
	return result

def get_corner_frequencies(frequencies):
	"""
	Returns corner frequencies, that can be used as cutoff frequencies for the
	highpass and lowpass filters of a filterbank, so that the input is divided
	into frequency bands with the given center frequencies.
	The returned list of corner frequencies is one shorter than the given sequence
	of center frequencies, as the corner frequencies are between the center
	frequencies.
	@param frequencies: a sequence of center frequencies
	@retval : a list of corner frequencies
	"""
	return [(frequencies[i] - frequencies[i - 1]) / (math.log(frequencies[i] / frequencies[i - 1])) for i in range(1, len(frequencies))]

def refine_maximum(x_data, y_data):
	"""
	refines a maximum with quadratic interpolation
	@param x_data: a sequence of three x-axis samples that correspond to the given y_data
	@param y_data: a sequence of three y-axis samples, where the middle sample is the found maximum of the function
	@retval : a tuple with the x and the y value of the refined maximum
	"""
	x0, x1, x2 = x_data
	y0, y1, y2 = y_data
	matrix = [(x0 ** 2, x0, 1.0),
	          (x1 ** 2, x1, 1.0),
	          (x2 ** 2, x2, 1.0)]
	vector = [y0, y1, y2]
	a, b, c = numpy.linalg.solve(matrix, vector)
	x = (-b / (2.0 * a))
	y = a * x ** 2 + b * x + c
	return x, y

def get_delay(excitation, response):
	delays = []
	inverted = []
	crosscorrelation = sumpf.modules.CorrelateSignals(signal1=response, signal2=excitation, mode=sumpf.modules.CorrelateSignals.SPECTRUM).GetOutput()
	# find the maximum of the cross correlation
	for channel in crosscorrelation.GetChannels():
		maximum_index = channel.index(max(channel))
		if maximum_index > len(channel) // 2:
			maximum_index -= len(channel)
		minimum_index = channel.index(min(channel))
		if minimum_index > len(channel) // 2:
			minimum_index -= len(channel)
		shift = maximum_index
		if abs(channel[maximum_index]) < abs(channel[minimum_index]) and abs(minimum_index) < abs(maximum_index):
			shift = minimum_index
			inverted.append(True)
		else:
			inverted.append(False)
		x_data = tuple(range(shift - 1, shift + 2))
		delay = refine_maximum(x_data, [channel[i] for i in x_data])[0] / crosscorrelation.GetSamplingRate()
		delays.append(delay)
	return delays, inverted

def align_signals(excitation, response, highpass_frequency=None):
	"""
	Shifts the response signal, so that it aligns best with the excitation signal.
	The returned excitation and response signal are cropped by the shift samples.
	"""
	if len(excitation) % 2 != 0:
		excitation = excitation[0:-1]
		response = response[0:-1]
	# apply a high pass to remove dc-offset
	filtered_excitation, filtered_response = excitation, response
	filtered_response_spectrum = None
	if highpass_frequency is not None and highpass_frequency > 0.0:
		excitation_spectrum = sumpf.modules.FourierTransform(signal=excitation).GetSpectrum()
		response_spectrum = sumpf.modules.FourierTransform(signal=response).GetSpectrum()
		highpass = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH_HIGHPASS(frequency=highpass_frequency, order=1), resolution=excitation_spectrum.GetResolution(), length=len(excitation_spectrum)).GetSpectrum()
		copied_highpass = sumpf.modules.CopySpectrumChannels(input=highpass, channelcount=len(excitation_spectrum.GetChannels())).GetOutput()
		filtered_excitation_spectrum = excitation_spectrum * copied_highpass
		filtered_response_spectrum = response_spectrum * copied_highpass
		filtered_excitation = sumpf.modules.InverseFourierTransform(spectrum=filtered_excitation_spectrum).GetSignal()
		filtered_response = sumpf.modules.InverseFourierTransform(spectrum=filtered_response_spectrum).GetSignal()
	else:
		filtered_response_spectrum = sumpf.modules.FourierTransform(signal=filtered_response).GetSpectrum()
	# calculate the cross correlation to get the time shift between excitation and response
	delays, inverted = get_delay(excitation=filtered_excitation, response=filtered_response)
	delay_filters = sumpf.modules.MergeSpectrums()
	for d in delays:
		delay_filter = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.CONSTANT_GROUP_DELAY(delay=-d), resolution=filtered_response_spectrum.GetResolution(), length=len(filtered_response_spectrum)).GetSpectrum()
		delay_filters.AddInput(delay_filter)
	inversion_factors = []
	shifted_response_spectrum = filtered_response_spectrum * delay_filters.GetOutput()
	shifted_response = sumpf.modules.InverseFourierTransform(spectrum=shifted_response_spectrum).GetSignal()
	# crop the signals to remove artifacts from shifing
	crop = max(int(round((max(delays) * excitation.GetSamplingRate()))), 1)
	cropped_excitation = filtered_excitation[crop:-crop]
	cropped_response = shifted_response[crop:-crop]
	# invert the response channels if necessary
	for i in inverted:
		if i:
			inversion_factors.append(-1.0)
		else:
			inversion_factors.append(1.0)
	cropped_response = sumpf.modules.AmplifySignal(input=cropped_response, factor=inversion_factors).GetOutput()
	# mach feierabend
	sumpf.collect_garbage()
	return cropped_excitation, cropped_response

def append_zeros(signal, length=None):
	"""
	Appends zeros until the signal has the given length. If no length is given,
	zeros will be appended until the length is a power of 2.
	"""
	if length is None:
		length = 2 ** int(math.ceil(math.log(len(signal), 2)))
	zeros = length - len(signal)
	result = sumpf.Signal(channels=tuple([c + (0.0,) * zeros for c in signal.GetChannels()]),
	                      samplingrate=signal.GetSamplingRate(),
	                      labels=signal.GetLabels())
	return result

