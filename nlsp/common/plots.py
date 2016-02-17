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
    pyplot.xticks(fontsize="large")
    pyplot.yticks(fontsize="large")
    pyplot.ylim((0.01, 1000.0))
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


def plot_groupdelayandmagnitude(data, show=True, save=False, name=None):
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
                pyplot.subplot(2,1,1)
                pyplot.title("Frequency")
                pyplot.loglog(x_data, d.GetMagnitude()[i], label=d.GetLabels()[i])
                pyplot.subplot(2,1,2)
                pyplot.title("Group delay")
                pyplot.semilogx(x_data, d.GetGroupDelay()[i], label=d.GetLabels()[i])
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

def relabelandplot(input,label,show=True,save=False,name=None):
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


def plot_array(input_array,label_array=None,save=False,name=None):
    """
    Helper function to plot array
    :param input_array: the input array of signal or spectrum
    :param label_array: the array of labels
    :return: the plot of the input array with labels
    """
    if label_array is None:
        label_array = []
        for input in input_array:
            label_array.append(str(input.GetLabels()))
    for input,label in zip(input_array,label_array):
        relabelandplot(input,label,False,save,name)
    show()
