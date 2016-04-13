import numpy as np
import adaptfilt
import sumpf
import nlsp

def lms(input_signal, desired_output, filter_taps, step, leak=0, initCoeffs=None, N=None):

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
        N = len(u)-M+1
        w = init[channel]
        y = np.zeros(N)  # Filter output
        e = np.zeros(N)  # Error signal
        for n in xrange(N):
            x = np.flipud(u[n:n+M])  # Slice to get view of M latest datapoints
            y[n] = np.dot(x, w)
            e[n] = d[n+M-1] - y[n]
            w = leakstep * w + step * x * e[n]
        W.append(w)
    return W



def nlms(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None):

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
        N = len(u)-M+1
        w = init[channel]
        for n in xrange(N):
            x = np.flipud(u[n:n+M])  # Slice to get view of M latest datapoints
            y = np.dot(x, w)
            e = d[n+M-1] - y
            normFactor = 1./(np.dot(x, x) + eps)
            w = leakstep * w + step * normFactor * x * e
        W.append(w)
    return W

def ap(input_signal, desired_output, filter_taps, step, proj_order=1, eps=0.001, leak=0, initCoeffs=None, N=None):

    d = desired_output
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
        y = np.zeros(N)  # Filter output
        e = np.zeros(N)  # Error signal
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
        W.append(w)

    return W

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

def multichannel_nlms_ideal(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None, plot = False):

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


# def multichannel_nlms(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None):
#
#     d = desired_output
#     M = filter_taps
#     channels = len(input_signal)
#     W = []
#     if initCoeffs is None:
#         init = np.zeros((channels,M))
#     else:
#         init = initCoeffs
#     leakstep = (1 - step*leak)
#
#     u1 = input_signal[0]
#     u2 = input_signal[1]
#     u3 = input_signal[2]
#     if N is None:
#         N = len(u1)-M+1
#     w1 = init[0]           # Initial coefficients
#     w2 = init[1]           # Initial coefficients
#     w3 = init[2]           # Initial coefficients
#     y1 = np.zeros(N)  # Filter output
#     y2 = np.zeros(N)  # Filter output
#     y3 = np.zeros(N)  # Filter output
#     e = np.zeros((channels,N))  # Error signal
#     for n in xrange(N):
#         x1 = np.flipud(u1[n:n+M])  # Slice to get view of M latest datapoints
#         x2 = np.flipud(u2[n:n+M])  # Slice to get view of M latest datapoints
#         x3 = np.flipud(u3[n:n+M])  # Slice to get view of M latest datapoints
#         y1[n] = np.dot(x1, w1)
#         y2[n] = np.dot(x2, w2)
#         y3[n] = np.dot(x3, w3)
#         y = np.sum([y1[n],y2[n],y3[n]],axis=0)
#         e[0][n] = d[n+M-1] - y
#
#         normFactor1 = 1./(np.dot(x1, x1) + eps)
#         normFactor2 = 1./(np.dot(x2, x2) + eps)
#         normFactor3 = 1./(np.dot(x3, x3) + eps)
#         w1 = leakstep * w1 + step * normFactor1 * x1 * e[0][n]
#         w2 = leakstep * w2 + step * normFactor2 * x2 * e[0][n]
#         w3 = leakstep * w3 + step * normFactor3 * x3 * e[0][n]
#     W.append(w1)
#     W.append(w2)
#     W.append(w3)
#     return W

def multichannel_nlms(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None, plot = False):

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