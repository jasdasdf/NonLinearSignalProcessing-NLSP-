import collections
import math
import sumpf
import numpy
import matplotlib.pyplot as pyplot

scale_log = False
axis = pyplot.subplot(111)

def dBlabel(y, pos):
	if y <= 0.0:
		return "0.0"
	else:
		spl = 20.0 * math.log(y, 10)
		return "%.1f dB" % spl

def log():
	dBformatter = pyplot.FuncFormatter(dBlabel)
	axis.set_xscale("log")
	axis.set_yscale("log")
	axis.yaxis.set_major_formatter(dBformatter)
#	axis.yaxis.set_minor_formatter(dBformatter)
	globals()["scale_log"] = True

def reset_color_cycle():
	cc = axis._get_lines.color_cycle
	while cc.next() != "k":
		pass

def show():
	pyplot.show()
	globals()["axis"] = pyplot.subplot(111)
	if scale_log:
		log()

def _show():
	show()

def plot(data, legend=True, show=True):
#	image = pyplot.imread("data/Fels.png")
#	pyplot.figimage(image)
#	pyplot.imshow(image)
	if not isinstance(data, collections.Iterable):
		data = [data]
	if isinstance(data[0], sumpf.Spectrum):
		for d in data:
			# create x_data
			x_data = []
			for i in range(len(d)):
				x_data.append(i * d.GetResolution())
			# plot
			for i in range(len(d.GetMagnitude())):
				pyplot.plot(x_data, d.GetMagnitude()[i], label=d.GetLabels()[i])
#				pyplot.plot(x_data[0:len(x_data) // 2], d.GetPhase()[i][0:len(x_data) // 2], label=d.GetLabels()[i])
#				pyplot.plot(x_data, d.GetGroupDelay()[i], label=d.GetLabels()[i])
		pyplot.xlim((20.0, 40000.0))
	else:
		for d in data:
			# create x_data
			x_data = []
			for i in range(len(d)):
				x_data.append(float(i) / d.GetSamplingRate())
			# plot
			for i in range(len(d.GetChannels())):
				pyplot.plot(x_data, d.GetChannels()[i], label=d.GetLabels()[i])
	if legend:
		pyplot.legend(loc="best", fontsize="x-large")
	axis.set_xlabel("Frequeny [Hz]", fontsize="x-large")
#	axis.set_ylabel("Impedanz [dB rel. 1 Pa*s/m^3]", fontsize="x-large")
#	axis.set_ylabel("Z / Z0 [dB rel. 1 N*s/m^3]", fontsize="x-large")
#	axis.set_ylabel("Kalibrationsfaktor [dB rel. 1 Pa*s/m^3]", fontsize="x-large")
	pyplot.xticks(fontsize="large")
	pyplot.yticks(fontsize="large")
#	pyplot.ylim((0.01, 1000.0))
	if show:
		_show()

def plot_spectrogram(data):
	print
	x_data = []
	for i in range(len(data)):
		x_data.append(float(i) / data.GetSamplingRate())
	y_data = []
	for i in range(len(data.GetSpectrums()[0])):
		y_data.append(i * data.GetSpectrums()[0].GetResolution())
	color_data = []
	for s in data.GetSpectrums():
		color_data.append(s.GetMagnitude()[0])
	color_data = numpy.transpose(color_data)
	axis.set_yscale('symlog')
	axis.set_ylim(y_data[1], y_data[-1])
	axis.set_xlim(x_data[0], x_data[-1])
	x_axis = numpy.array(x_data)
	y_axis = numpy.array(y_data)
	color_grid = numpy.multiply(numpy.log10(color_data), 10.0)
	plot = axis.pcolormesh(x_axis, y_axis, color_grid)
	pyplot.colorbar(plot)
	show()

