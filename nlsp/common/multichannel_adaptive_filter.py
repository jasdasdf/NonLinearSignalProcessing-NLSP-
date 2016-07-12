import numpy as np
import sumpf
import nlsp

def multichannel_ap_ideal(input_signal, desired_output, filter_taps, step, proj_order=1, eps=0.001, leak=0, initCoeffs=None, N=None):

    d = desired_output
    out = sumpf.Signal(channels=(d,), samplingrate=48000.0, labels=("output",))
    M = filter_taps
    K = proj_order
    channels = len(input_signal)

    I = np.identity(K)  # Init. identity matrix for faster loop matrix inv.
    epsI = eps * np.identity(K)  # Init. epsilon identiy matrix

    W = []
    if initCoeffs is None:
        init = np.zeros((channels,M))
    else:
        init = initCoeffs
    leakstep = (1 - step*leak)

    for channel in range(channels):
        u = input_signal[channel]
        N = len(u)-M+1
        w = init[channel]
        for n in xrange(N):
            # Generate U matrix and D vector with current data
            U = np.zeros((M, K))
            for k in np.arange(K):
                U[:, (K-k-1)] = u[n+k:n+M+k]
            U = np.flipud(U)
            D = np.flipud(d[n+M-1:n+M+K-1])
            # Filter
            y = np.dot(U.T, w)
            e = D - y
            # Normalization factor
            normFactor = np.linalg.solve(epsI + np.dot(U.T, U), I)
            # Naive alternative
            # normFactor = np.linalg.inv(epsI + np.dot(U.T, U))
            w = leakstep * w + step * np.dot(U, np.dot(normFactor, e))
        d = d - y
        W.append(w)
    return W

def siso_nlms_multichannel(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None, plot = False):

    d = desired_output
    M = filter_taps
    channels = len(input_signal)
    W = []
    if initCoeffs is None:
        init = np.zeros((channels,M))
    else:
        init = initCoeffs
    leakstep = (1 - step*leak)

    for channel in range(channels):
        u = input_signal[channel]
        if N is None:
            N = len(u)-M+1
        w = init[channel]           # Initial coefficients
        y = np.zeros((channels,N))  # Filter output
        e = np.zeros((channels,N))  # Error signal
        for n in xrange(N):
            x = np.flipud(u[n:n+M])  # Slice to get view of M latest datapoints
            y[channel][n] = np.dot(x, w)
            e[channel][n] = d[n+M-1] - y[channel][n]

            normFactor = 1./(np.dot(x, x) + eps)
            w = leakstep * w + step * normFactor * x * e[channel][n]
        if plot is True:
            nlsp.common.plots.plot_simplearray(range(len(e[channel])),e[channel],"x","y","e")
        d = d - np.dot(x, w)
        W.append(w)
    return W

def miso_nlms_multichannel(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None, plot = False):

    d = desired_output
    M = filter_taps
    channels = len(input_signal)
    W = []
    if N is None:
        N = len(input_signal[0])-M+1
    if initCoeffs is None:
        init = np.zeros((channels,M))
    else:
        init = initCoeffs
    leakstep = (1 - step*leak)
    u = []                      # input signal array
    w = []                      # filter coefficients array
    for channel in range(channels):
        u.append(input_signal[channel])
        w.append(init[channel])
    E = np.zeros(N)
    for n in xrange(N):
        normfac = [0,]*channels
        x = np.zeros((channels,M))
        y = np.zeros((channels,M))
        for channel in range(channels):
            x[channel] = np.flipud(u[channel][n:n+M])
            normfac[channel] = 1./(np.dot(x[channel], x[channel]) + eps)
            y[channel] = np.dot(x[channel], w[channel])

        Y = np.sum(y,axis=0)
        e = d[n+M-1] - Y
        E[n] = np.sum(e)
        for channel in range(channels):
            w[channel] = leakstep * w[channel] + step * normfac[channel] * x[channel] * e
    if plot is True:
        nlsp.common.plots.plot_simplearray(range(len(E)),E,"x","y","e")
    for channel in range(channels):
        W.append(w[channel])
    return W