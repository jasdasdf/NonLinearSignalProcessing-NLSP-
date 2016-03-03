import sumpf
import nlsp
import os

from_format = sumpf.modules.SignalFile.NUMPY_NPZ
to_format = sumpf.modules.SignalFile.WAV_FLOAT
directory = "F:/nl_recordings/rec_3/"

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

for filename in get_filepaths(directory):
    print filename
    load = sumpf.modules.SignalFile(filename=filename,
                                    format=from_format)
    save = sumpf.modules.SignalFile(filename=filename,
                                    signal=load.GetSignal(),
                                    format=to_format)