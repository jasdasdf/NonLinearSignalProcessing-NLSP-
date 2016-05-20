import sumpf
import nlsp
import os

from_format = sumpf.modules.SignalFile.NUMPY_NPZ
to_format = sumpf.modules.SignalFile.WAV_FLOAT
directory = "C:/Users/diplomand.8/Desktop/nl_recordings/rec_5_ls/noise/"

def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

def convert_audio():
    for filename in get_filepaths(directory):
        print filename
        load = sumpf.modules.SignalFile(filename=filename,
                                        format=from_format)
        print len(load.GetSignal())
        save = sumpf.modules.SignalFile(filename=filename,
                                        signal=load.GetSignal(),
                                        format=to_format)

def generate_audio():
    sampling_rate = 48000.0
    start_freq = 20.0
    stop_freq = 20000.0
    length = 2**18
    normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
    uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
    gamma = sumpf.modules.NoiseGenerator.GammaDistribution()
    pink = sumpf.modules.NoiseGenerator.PinkNoise()
    wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=normal)
    wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=uniform)
    wgn_gamma = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=gamma)
    wgn_pink = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=pink)

    save_normal = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/wgn_normal_18",
                                        signal=wgn_normal.GetOutput(),
                                        format=sumpf.modules.SignalFile.NUMPY_NPZ)
    save_uniform = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/wgn_uniform_18",
                                        signal=wgn_uniform.GetOutput(),
                                        format=sumpf.modules.SignalFile.NUMPY_NPZ)
    save_gamma = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/wgn_gamma_18",
                                        signal=wgn_gamma.GetOutput(),
                                        format=sumpf.modules.SignalFile.NUMPY_NPZ)
    save_pink = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/wgn_pink_18",
                                        signal=wgn_pink.GetOutput(),
                                        format=sumpf.modules.SignalFile.NUMPY_NPZ)

def generate_sweep():
    sampling_rate = 44100
    length = 2**18
    fade_in = 0.02
    fade_out = 0.02
    sine_sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate,length=length,fade_in=fade_in,fade_out=fade_out)
    dummy = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=sampling_rate,length=len(sine_sweep.GetOutput())).GetSignal()
    sine_double = sumpf.modules.MergeSignals(signals=[sine_sweep.GetOutput(),sine_sweep.GetOutput()]).GetOutput()
    sine_left = sumpf.modules.MergeSignals(signals=[sine_sweep.GetOutput(),dummy]).GetOutput()
    sine_right = sumpf.modules.MergeSignals(signals=[dummy,sine_sweep.GetOutput()]).GetOutput()
    sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/sinesweep_double_withfading",
                                              signal=sine_double,
                                              format=sumpf.modules.SignalFile.WAV_FLOAT)
    sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/sinesweep_left_withfading",
                                              signal=sine_left,
                                              format=sumpf.modules.SignalFile.WAV_FLOAT)
    sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/sinesweep_right_withfading",
                                              signal=sine_right,
                                              format=sumpf.modules.SignalFile.WAV_FLOAT)

def analyze_for_thomas():
    sampling_rate = 48000.0
    length = 2**16
    branches = 3
    path = "C:/Users/diplomand.8/Desktop/thomas_sweep/new/"

    file_input = "C:/Users/diplomand.8/Desktop/thomas_sweep/new/input.wav"
    load_input = sumpf.modules.SignalFile(filename=file_input, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
    sweep_input = load_input

    listdir = os.listdir(path)
    for file in listdir:

        file_output = os.path.join(path,file)
        load_output = sumpf.modules.SignalFile(filename=file_output, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
        load_output = nlsp.change_length_signal(load_output,len(load_input))
        sweep_output = load_output
        print file_output
        sweep_output_spec = sumpf.modules.FourierTransform(sweep_output).GetSpectrum()
        rev_spec = sumpf.modules.RegularizedSpectrumInversion(spectrum=sumpf.modules.FourierTransform(sweep_input).GetSpectrum(),start_frequency=20.0,stop_frequency=20000.0).GetOutput()
        nl_tf = sumpf.modules.MultiplySpectrums(rev_spec,sweep_output_spec)
        nl_ir = sumpf.modules.InverseFourierTransform(nl_tf.GetOutput()).GetSignal()
        # nlsp.common.plots.plot(nl_ir)

        direct = sumpf.modules.CutSignal(nl_ir,stop=int(3*nl_ir.GetSamplingRate())).GetOutput()
        harmonics = sumpf.modules.CutSignal(nl_ir,start=int(3*nl_ir.GetSamplingRate())).GetOutput()
        print len(harmonics)

        print nlsp.calculateenergy_time(harmonics)
        print

branches = 5
file_input = "C:/Users/diplomand.8/Desktop/thomas_sweep/temp/sinesweep_double.wav"
load_input = sumpf.modules.SignalFile(filename=file_input, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
signal = sumpf.modules.SplitSignal(data=load_input,channels=[0]).GetOutput()
sampling_rate = 44100
length = 2**18
fade_in = 0.0
fade_out = 0.0
sine_sweep = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate,length=length,fade_in=fade_in,fade_out=fade_out)
filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=signal)
ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=signal,
                                                 nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind,
                                                 max_harmonics=range(1,branches+1))
filter,func = nlsp.nonlinearconvolution_powerseries_temporalreversal(sine_sweep,ref_nlsystem.GetOutput(),branches)
iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=signal,
                                                 nonlinear_functions=func,
                                                 filter_irs=filter,
                                                 max_harmonics=range(1,branches+1))
print nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem.GetOutput())
# generate_sweep()
# convert_audio()