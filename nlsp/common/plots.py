import collections
import math
import sumpf
import nlsp
import matplotlib.pyplot as pyplot
import os

max_freq = 40000.0
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


def plot(data, legend=True, show=True, save=False, name=None):
    if not isinstance(data, collections.Iterable):
        data = [data]
    if isinstance(data[0], sumpf.Spectrum):
        log()
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
        pyplot.xlim((0.0, max_freq))
        axis.set_xlabel("Frequeny [Hz]", fontsize="x-large")
    else:
        for d in data:
            # create x_data
            x_data = []
            for i in range(len(d)):
                x_data.append(float(i) / d.GetSamplingRate())
            # plot
            for i in range(len(d.GetChannels())):
                pyplot.plot(x_data, d.GetChannels()[i], label=d.GetLabels()[i])
        axis.set_xlabel("Time [s]", fontsize="x-large")
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if save is True:
        location = "C:/Users/diplomand.8/OneDrive/Pictures/"
        fig = os.path.join(location,name)
        pyplot.savefig(fig, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None)
    else:
        if show:
            _show()


def plot_groupdelayandmagnitude(data, legend=True, show=True, save=False, name=None):
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
                ax = pyplot.subplot(2,1,1)
                pyplot.title("Frequency")
                pyplot.loglog(x_data, d.GetMagnitude()[i], label=d.GetLabels()[i])
                pyplot.subplot(2,1,2,sharex=ax)
                pyplot.title("Group delay")
                pyplot.semilogx(x_data, d.GetGroupDelay()[i], label=d.GetLabels()[i])
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if save is True:
        location = "C:/Users/diplomand.8/OneDrive/Pictures/"
        fig = os.path.join(location,name)
        pyplot.savefig(fig, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None)
    else:
        if show:
            _show()

def plot_timeandfreq(data_time, data_freq, legend=True, show=True):
    if not isinstance(data_time, collections.Iterable):
        data_time = [data_time]
    if not isinstance(data_freq, collections.Iterable):
        data_freq = [data_freq]
    for d in data_freq:
        # create x_data
        x_data = []
        for i in range(len(d)):
            x_data.append(i * d.GetResolution())
        # plot
        for i in range(len(d.GetMagnitude())):
            pyplot.subplot(2,1,1)
            pyplot.title("Frequency")
            pyplot.loglog(x_data, d.GetMagnitude()[i], label=d.GetLabels()[i])
    axis.set_xlabel("Frequeny [Hz]", fontsize="x-large")
    for d in data_time:
        # create x_data
        x_data = []
        for i in range(len(d)):
            x_data.append(float(i) / d.GetSamplingRate())
        # plot
        for i in range(len(d.GetChannels())):
            pyplot.subplot(2,1,2)
            pyplot.title("Amplitude")
            pyplot.plot(x_data, d.GetChannels()[i], label=d.GetLabels()[i])
    axis.set_xlabel("Time [s]", fontsize="x-large")
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if show:
        _show()

def relabelandplot(input,label=None,show=True,save=False,name=None):
    """
    Relabel the input signal or spectrum and plot
    :param input: the input signal or spectrum
    :param label: the label text
    :param show: True or False
    :return: plots the given input with label
    """
    relabelled = nlsp.relabel(input,label)
    if isinstance(relabelled, sumpf.Spectrum):
        log()
    plot(relabelled,show=show,save=save,name=name)

def relabelandplotphase(input,label,show=True,save=False,name=None):
    """
    Relabel the input signal or spectrum and plot
    :param input: the input signal or spectrum
    :param label: the label text
    :param show: True or False
    :return: plots the given input with label
    """
    relabelled = nlsp.relabel(input,label)
    if isinstance(relabelled, sumpf.Spectrum):
        log()
    plot_groupdelayandmagnitude(relabelled,show=show)


def plot_array(input_array,label_array=None,save=False,name=None):
    """
    Helper function to plot array
    :param input_array: the input array of signal or spectrum
    :param label_array: the array of labels
    :return: the plot of the input array with labels
    """
    if label_array is None:
        label_array = [None,] * len(input_array)
    for input,label in zip(input_array,label_array):
        relabelandplot(input,label,False,save,name)
    show()

def plot_simplearray(x_array,y_array,label,show=True):
    pyplot.plot(x_array,y_array,label=label)
    if show is True:
        pyplot._show()

def plot_histogram(data, legend=True, show=True, save=False, name=None):
    if not isinstance(data, collections.Iterable):
        data = [data]
    for d in data:
        for i in range(len(d.GetChannels())):
            pyplot.hist(d.GetChannels()[i], bins=500)
    axis.set_xlabel("Value", fontsize="x-large")
    if legend:
        pyplot.legend(loc="best", fontsize="x-large")
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    if save is True:
        location = "C:/Users/diplomand.8/OneDrive/Pictures/"
        fig = os.path.join(location,name)
        pyplot.savefig(fig, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None)
    else:
        if show:
            _show()

def plot_timeandfreq_array(input_array,show=True):
    if isinstance(input_array, list) != True:
        array1 = []
        array1.append(input_array)
    else:
        array1 = input_array
    for one in array1:
        if isinstance(one,sumpf.Signal):
            one_signal = one
            one_spectrum = sumpf.modules.FourierTransform(one).GetSpectrum()
        else:
            one_signal = sumpf.modules.InverseFourierTransform(one).GetSignal()
            one_spectrum = one
        plot_timeandfreq(one_signal,one_spectrum,show=False)
    if show is True:
        _show()