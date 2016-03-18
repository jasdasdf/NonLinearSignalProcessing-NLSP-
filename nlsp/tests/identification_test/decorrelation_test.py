import nlsp
import sumpf
import nlsp.common.plots as plot

def test_decorrelation():
    input = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(),samplingrate=48000.0,
                                 length=2**20).GetSignal()
    # input = nlsp.NovakSweepGenerator_Sine()
    # input = input.GetOutput()
    decorr_input,k,mu = nlsp.wgn_hgm_decorrelate(input,5)
    for i in range(len(decorr_input)):
        for j in range(len(decorr_input)):
            cross_corr = sumpf.modules.CorrelateSignals(signal1=decorr_input[i],signal2=decorr_input[j],mode=sumpf.modules.CorrelateSignals.SAME).GetOutput()
            # csd = sumpf.modules.FourierTransform(cross_corr).GetSpectrum()
            # plot.plot(cross_corr)
            print nlsp.calculateenergy_time(cross_corr),i,j
    print k

# test_decorrelation()