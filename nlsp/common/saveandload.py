import sumpf
import nlsp
import numpy
import os

location = "C:/Users/diplomand.8/Desktop/evaluation/filter_kernel/"

def save_systemidentification(method,nlsystem,filterkernels):
    branches = len(filterkernels)
    str_method = str(method)
    f,func,rest,rest2 = str_method.split()
    filename = '_'.join((nlsystem, func, str(branches)))
    file = os.path.join(location,filename)
    kernels = sumpf.modules.MergeSignals(signals=filterkernels).GetOutput()
    kernels.GetChannels()
    sumpf.modules.SignalFile(filename=file, signal=kernels, format=sumpf.modules.SignalFile.NUMPY_NPZ)

def load_systemidentification(method,nlsystem,branches):
    str_method = str(method)
    f,func,rest,rest2 = str_method.split()
    filename = '_'.join((nlsystem, func, str(branches)))
    filename = ''.join((filename,".npz"))
    file = os.path.join(location,filename)
    if os.path.isfile(file):
        filter_impulse_response = sumpf.modules.SignalFile(filename=file, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
        filter_ir = nlsp.multichanneltoarray(filter_impulse_response)
        if "power" in func:
            nl_functions = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
        elif "cheby" in func:
            nl_functions = nlsp.nl_branches(nlsp.function_factory.chebyshev1_polynomial,branches)
        elif "legendre" in func:
            nl_functions = nlsp.nl_branches(nlsp.function_factory.legrendre_polynomial,branches)
        elif "hermite" in func:
            nl_functions = nlsp.nl_branches(nlsp.function_factory.hermite_polynomial,branches)
    else:
        filter_ir = None
        nl_functions = None
    return filter_ir, nl_functions

def systemidentification(nlsystem,method,branches,input_generator,output):
    found_filter_spec,nl_functions = load_systemidentification(method,"powerhgm",branches)
    if found_filter_spec is None:
        found_filter_spec, nl_functions = method(input_generator,output,branches)
        save_systemidentification(method,nlsystem,found_filter_spec)
    return found_filter_spec, nl_functions
