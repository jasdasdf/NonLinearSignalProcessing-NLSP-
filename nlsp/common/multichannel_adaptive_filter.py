import numpy as np
import adaptfilt
import sumpf
import nlsp

def multichannel_lms(input_signal, desired_output, filter_taps, step, leak=0, initCoeffs=None, N=None):

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



def multichannel_nlms(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None):

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

def multichannel_ap(input_signal, desired_output, filter_taps, step, proj_order=1, eps=0.001, leak=0, initCoeffs=None, N=None):

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

def multichannel_nlms_ideal(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None):

    d = desired_output
    out = sumpf.Signal(channels=(d,), samplingrate=48000.0, labels=("output",))
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

            normFactor = 1./(np.dot(x, x) + eps)
            w = leakstep * w + step * normFactor * x * e[n]
            y[n] = np.dot(x, w)
        # d = d - y[n]
        W.append(w)
    return W
