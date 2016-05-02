import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**16
fade_out = 0.00
fade_in = 0.00
branches = 5
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
pink = sumpf.modules.NoiseGenerator.PinkNoise()
laplace = sumpf.modules.NoiseGenerator.LaplaceDistribution(mean=0.0,scale=0.3)

Plot = False
Save = False

sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)
wgn_pink = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=pink)
wgn_laplace = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=laplace)

def generate_excitation():
    sines = nlsp.relabel(sine.GetOutput(),"sine_sweep")
    coss = nlsp.relabel(cos.GetOutput(),"cos_sweep")
    wgn_normals = nlsp.relabel(wgn_normal.GetOutput(),"white_normal")
    wgn_uniforms = nlsp.relabel(wgn_uniform.GetOutput(), "white_uniform")
    wgn_pinks = nlsp.relabel(wgn_pink.GetOutput(),"white_pink")
    wgn_laplaces = nlsp.relabel(wgn_laplace.GetOutput(),"white_laplace")
    inputs = [sines,coss,wgn_normals,wgn_uniforms,wgn_pinks,wgn_laplaces]
    for input in inputs:
        sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/evaluation/filter_kernel/mp3/%s" %str(input.GetLabels()[0]),
                                 signal=input,format=sumpf.modules.SignalFile.WAV_FLOAT)
        print input

def simulatecodec_usinghgm():
    ip_sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/evaluation/filter_kernel/mp3/input/sine_sweep.wav")
    op_sine = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/evaluation/filter_kernel/mp3/output/sine_sweep.mp3")
    print ip_sine.GetSignal()
    print op_sine.GetSignal()


simulatecodec_usinghgm()
# generate_excitation()

