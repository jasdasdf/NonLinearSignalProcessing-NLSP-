import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000
length = 2**18
start_freq = 20.0
stop_freq = 20000.0
echo_decay = 0.1
branches = 5
shift = 800

normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.5)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
pink = sumpf.modules.NoiseGenerator.PinkNoise()
laplace = sumpf.modules.NoiseGenerator.LaplaceDistribution(mean=0.0,scale=0.3)

sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq)
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
nl_system_iden_excitation = sine
system_identification_alg = nlsp.nonlinearconvolution_powerseries_temporalreversal
speech = wgn_pink.GetOutput()

def echoic_nonlinear_chamber(input):
    hgm = nlsp.construct_hgm(kernelfile=nl_system)
    hgm.SetInput(input)
    s1 = sumpf.modules.ShiftSignal(signal=hgm.GetOutput(),shift=shift,circular=False).GetOutput()
    s1_decay = sumpf.modules.AmplifySignal(input=s1,factor=echo_decay).GetOutput()
    s = s1_decay + hgm.GetOutput() + speech
    return s

def nlsystem(branches,excitation,system_identification_alg):
    ref_hgm = nlsp.construct_hgm(kernelfile=nl_system)
    ref_hgm.SetInput(excitation.GetOutput())
    ref_output = ref_hgm.GetOutput()
    kernel, function = system_identification_alg(excitation,ref_output,branches)
    iden_hgm = nlsp.HammersteinGroupModel_up(nonlinear_functions=function,filter_irs=kernel,max_harmonics=range(1,branches+1))
    return iden_hgm,ref_hgm

def nlechocancellation(input):
    iden_nl_system, ref_nl_system = nlsystem(branches=branches,excitation=nl_system_iden_excitation,system_identification_alg=system_identification_alg)
    iden_nl_system.SetInput(input)
    echoic_op = echoic_nonlinear_chamber(input)
    desired_op = echoic_op - iden_nl_system.GetOutput()
    kernel, nlfunction = nlsp.adaptive_identification_legendre(iden_nl_system.GetOutput(),desired_op,branches=1,filtertaps=2**10)
    iden_lin_system = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlfunction,filter_irs=kernel)
    iden_lin_system.SetInput(iden_nl_system.GetOutput())
    determined_output = iden_lin_system.GetOutput() + iden_nl_system.GetOutput()
    speech = determined_output - desired_op
    return speech

iden_speech = nlechocancellation(input=wgn_normal.GetOutput())
nlsp.common.plots.plot(iden_speech,show=False)
nlsp.common.plots.plot(speech,show=True)
print nlsp.snr(iden_speech,speech)

