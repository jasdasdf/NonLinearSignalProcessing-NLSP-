import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000
length = 2**19
start_freq = 20.0
stop_freq = 20000.0

normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.5)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
pink = sumpf.modules.NoiseGenerator.PinkNoise()
laplace = sumpf.modules.NoiseGenerator.LaplaceDistribution(mean=0.0,scale=0.3)

sine = sumpf.modules.SweepGenerator(length=length, start_frequency=start_freq, stop_frequency=stop_freq,
                                    samplingrate=sampling_rate)
cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq)
wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)
wgn_pink = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=pink)
wgn_laplace = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=laplace)
nl_system = "C:/Users/diplomand.8/Desktop/evaluation/filter_kernel/LS_nonlinearconvolution_powerseries_temporalreversal_3_261948.npz"

def generate_nlecho(input):
    # d1 = sumpf.modules.ImpulseGenerator(delay=0,samplingrate=sampling_rate,length=length).GetSignal()
    # d2 = sumpf.modules.ImpulseGenerator(delay=0.2,samplingrate=sampling_rate,length=length).GetSignal()
    # d = sumpf.modules.AddSignals(signal1=d1, signal2=d2).GetOutput()
    # hgm = nlsp.construct_hgm(kernelfile=nl_system)
    # hgm.SetInput(input)
    # signal = sumpf.modules.FourierTransform(hgm.GetOutput()).GetSpectrum()
    # echo = sumpf.modules.FourierTransform(d).GetSpectrum()
    # signalandecho = sumpf.modules.MultiplySpectrums(signal,echo).GetOutput()
    # signalandecho = sumpf.modules.InverseFourierTransform(signalandecho).GetSignal()


    #alternative method
    hgm = nlsp.construct_hgm(kernelfile=nl_system)
    hgm.SetInput(input)
    s1 = sumpf.modules.ShiftSignal(signal=hgm.GetOutput(),shift=10,circular=False).GetOutput()
    s2 = sumpf.modules.ShiftSignal(signal=hgm.GetOutput(),shift=30,circular=False).GetOutput()
    s = s1 + s2 + hgm.GetOutput()
    signalandecho = s
    return signalandecho

def nlechocanceller(input,output,init_kernel=None):
    hgm = nlsp.construct_hgm(kernelfile=nl_system)
    hgm.SetInput(input)
    kernel,nlfunc = nlsp.adaptive_identification_powerseries(hgm.GetOutput(),output,branches=1,init_coeffs=init_kernel)
    iden_hgm = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlfunc,filter_irs=kernel)
    iden_hgm.SetInput(hgm.GetOutput())
    return iden_hgm.GetOutput(),kernel

init_kernel = None
inputg = [wgn_normal.GetOutput()]
for input in inputg:
    echo = generate_nlecho(input)
    signal = sumpf.modules.SweepGenerator(samplingrate=sampling_rate,length=length).GetSignal()
    output = echo + signal
    echoadded,init_kernel = nlechocanceller(input,output,init_kernel)
    det_signal = output - echoadded
    # plot.relabelandplot(echo,"echo",show=False)
    # plot.relabelandplot(signal,"signal",show=False)
    # plot.relabelandplot(output,"echo+signal",show=False)
    # plot.relabelandplot(det_signal,"identified",show=True)
    print nlsp.snr(det_signal,signal)
    print nlsp.snr(output,signal)
    print
