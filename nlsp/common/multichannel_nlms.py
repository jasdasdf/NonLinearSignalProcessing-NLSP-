import numpy as np

def multichannel_nlms(input_signal, desired_output, filter_taps, step, eps=0.001, leak=0, initCoeffs=None, N=None):

    d = desired_output
    M = filter_taps
    channels = len(input_signal)
    W = []
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
        W.append(w)
    return W
