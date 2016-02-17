import numpy
import sumpf
import nlsp
# import common.plot as plot

def wgn_hgm_decorrelate(input,branches,total_branches):
    k_matrix = numpy.zeros((total_branches,total_branches))
    mu_matrix = []
    def kay(n,m):
        k = 1
        for i in range(n,m):
            num = nlsp.NonlinearFunction.power_series(i+m+1,input).GetOutput()
            den = nlsp.NonlinearFunction.power_series(2*i,input).GetOutput()
            k_matrix[n-1][i-1] = kay(n,i)
            k = numpy.multiply(kay(n,i),numpy.divide(sumpf.modules.SignalMean(num).GetMean(),sumpf.modules.SignalMean(den).GetMean()))
        return float(k)
    dummy = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=input.GetSamplingRate(),length=len(input)).GetSignal()
    for branch in range(1,branches+1):
        power = nlsp.NonlinearFunction.power_series(branch,input)
        core = sumpf.modules.AmplifySignal(input=power.GetOutput(),factor=kay(branch,branches)).GetOutput()
        if branch %2 == 0:
            mu = sumpf.modules.SignalMean(signal=input).GetMean()
            mu = sumpf.modules.ConstantSignalGenerator(value=float(mu[0]),samplingrate=core.GetSamplingRate(),length=len(core)).GetSignal()
            mu_matrix.append(sumpf.modules.FourierTransform(mu).GetSpectrum())
            comb = core + mu
        else:
            mu = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=core.GetSamplingRate(),length=len(core)).GetSignal()
            mu_matrix.append(sumpf.modules.FourierTransform(mu).GetSpectrum())
            comb = core
        core = dummy + comb
    k_matrix[total_branches-1][total_branches-1] = kay(total_branches,total_branches)
    return core,k_matrix,mu_matrix



def wgn_hgm_identification(input_wgn,output_wgn,branches):
    l = []
    for branch in range(1,branches+1):
        # decorrelate = nlsp.NonlinearFunction.hermite_polynomial(branch,input_wgn)
        decorrelate,k_matrix,mu_matrix = wgn_hgm_decorrelate(input_wgn,branch,branches)
        cross_corr = sumpf.modules.CorrelateSignals(signal1=decorrelate,signal2=output_wgn,mode=sumpf.modules.CorrelateSignals.SAME).GetOutput()
        num = sumpf.modules.FourierTransform(cross_corr).GetSpectrum()
        den = sumpf.modules.FourierTransform(sumpf.modules.CorrelateSignals(signal1=decorrelate,
                                                                            signal2=decorrelate,mode=sumpf.modules.CorrelateSignals.SAME).GetOutput()).GetSpectrum()
        L = sumpf.modules.DivideSpectrums(spectrum1=num, spectrum2=den).GetOutput()
        kernel = sumpf.modules.InverseFourierTransform(L).GetSignal()
        signal = sumpf.Signal(channels=kernel.GetChannels(),samplingrate=input_wgn.GetSamplingRate(),labels=kernel.GetLabels())
        l.append(sumpf.modules.FourierTransform(signal).GetSpectrum())
    print k_matrix
    print mu_matrix
    print l
    # A = []
    # for row in range(0,branches):
    #     for column in range(0,branches):
    #         temp = sumpf.modules.AmplifySpectrum(input=l[row],factor=k_matrix[row][column]).GetOutput()
    #         A.append(temp)
    # for a in range(0,len(A)):
    #     print A[a]
    # return A

# signal = sumpf.modules.SineWaveGenerator(frequency=1.0,samplingrate=48000.0,length=48000).GetSignal()
# order = 5
# for n in range(1,order+1):
#     decorr_signal = wgn_hgm_decorrelate(signal,n)
#     plot.plot(decorr_signal,show=False)
# plot.show()