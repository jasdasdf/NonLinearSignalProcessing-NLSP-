import sumpf
import nlsp
import os

from_format = sumpf.modules.SignalFile.NUMPY_NPZ
to_format = sumpf.modules.SignalFile.WAV_FLOAT
directory = "C:/Users/diplomand.8/Desktop/nl_recordings/rec_4_ls/noise/"

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
        save = sumpf.modules.SignalFile(filename=filename,
                                        signal=load.GetSignal(),
                                        format=to_format)

def generate_audio():
    sampling_rate = 48000.0
    start_freq = 20.0
    stop_freq = 20000.0
    length = 2**16
    normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
    uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
    gamma = sumpf.modules.NoiseGenerator.GammaDistribution()
    wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=normal)
    wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=uniform)
    wgn_gamma = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, distribution=gamma)
    save_normal = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/wgn_normal_16",
                                        signal=wgn_normal.GetOutput(),
                                        format=sumpf.modules.SignalFile.NUMPY_NPZ)
    save_uniform = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/wgn_uniform_16",
                                        signal=wgn_uniform.GetOutput(),
                                        format=sumpf.modules.SignalFile.NUMPY_NPZ)
    save_gamma = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/wgn_gamma_16",
                                        signal=wgn_gamma.GetOutput(),
                                        format=sumpf.modules.SignalFile.NUMPY_NPZ)

convert_audio()