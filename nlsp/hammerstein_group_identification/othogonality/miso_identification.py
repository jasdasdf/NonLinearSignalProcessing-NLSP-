import sumpf
import nlsp
import common.plot as plot

def wgn_hgm_decorrelate(input_wgn,branches):
    for branch in range(1,branches+1):
        power = nlsp.NonlinearFunction.power_series(branch,input_wgn).GetOutput()
        def k(branch,branches):
            for i in range(branch,branches):
                temp_signal_1 = nlsp.NonlinearFunction.power_series(branch+branches,input_wgn)
                temp_signal_2 = nlsp.NonlinearFunction.power_series(2*branch,input_wgn)
                k = k(i,branch)*sumpf.modules.SignalMean(temp_signal_1.GetOutput())/\
                    sumpf.modules.SignalMean(temp_signal_2.GetOutput())


def wgn_hgm_identification(input_wgn,output_wgn,branches):
    l = []
    for branch in range(1,branches+1):
        decorrelate = nlsp.NonlinearFunction.hermite_polynomial(branch,input_wgn)
        cross_corr = sumpf.modules.CorrelateSignals(signal1=decorrelate.GetOutput(),signal2=output_wgn).GetOutput()
        num = sumpf.modules.FourierTransform(cross_corr).GetSpectrum()
        print cross_corr.GetSamplingRate()
        print cross_corr.GetDuration()

        den = sumpf.modules.FourierTransform(sumpf.modules.CorrelateSignals(signal1=decorrelate.GetOutput(),
                                                                            signal2=decorrelate.GetOutput()).GetOutput()).GetSpectrum()

        L = sumpf.modules.DivideSpectrums(spectrum1=num, spectrum2=den).GetOutput()
        l.append(sumpf.modules.InverseFourierTransform(L).GetSignal())
    return l
