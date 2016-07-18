# Modeling the acoustics of a car using the measurements done by Thomas for his Bachelor arbeit.

import sumpf
import nlsp
import os
import numpy
import pickle

source_directory = "C:\Users\diplomand.8\Desktop\car_modeling"
model_save_directory = "C:\Users\diplomand.8\Desktop\car_modeling\Models"
branches = 5

# Determine the model for the system to be identified
# 1. Read excitation and response files
# 2. Match excitation and response
# 3. Find appropriate identification method for the matched excitation and responses
# 4. Use the found identification method to model the system
# 5. Save the model with appropriate name

def read_excitations():
    """
    Read excitation and response files. And match the excitation and response.
    :return: the combined excitation and response
    """
    src = os.path.join(source_directory,"Excitations")
    excitation_path = os.path.join(src,"Excitation")
    response_path = os.path.join(src,"Response")
    excitation_files = os.listdir(excitation_path)
    response_files = os.listdir(response_path)
    for excitation_file in excitation_files:
        if excitation_file.rsplit('_')[1].find('LogeshSweep') != -1:
            sweep_ex_file = os.path.join(excitation_path,excitation_file)
        elif excitation_file.rsplit('_')[1].find('MLS') != -1:
            noise_ex_file = os.path.join(excitation_path,excitation_file)
    sweep_res = []
    noise_res = []
    for response_file in response_files:
        if 'LogeshSweep' in response_file.rsplit('_'):
            sweep_res.append(os.path.join(response_path,response_file))
        elif 'MLS' in response_file.rsplit('_'):
            noise_res.append(os.path.join(response_path,response_file))
    sweep_res.insert(0,sweep_ex_file)
    noise_res.insert(0,noise_ex_file)
    sweep_res.insert(0,'LogeshSweep')
    noise_res.insert(0,'MLS')
    excitations = [sweep_res,noise_res]
    return excitations

def system_identification_algorithm(excitations,branches=5):
    numpy.asarray(excitations)
    for excitation in excitations: # each type of identification
        code = excitation[0]
        excite = excitation[1]
        responses = excitation[2:]
        for response in responses:
            file_name = os.path.join(model_save_directory,response.split('\\')[-1])
            print file_name
            print
            if code is 'MLS': # adaptive system identification
                input = sumpf.modules.SignalFile(filename=excite,format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
                output = sumpf.modules.SignalFile(filename=response,format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
                input = sumpf.modules.SplitSignal(data=input,channels=[0]).GetOutput()
                output = sumpf.modules.SplitSignal(data=output,channels=[0]).GetOutput()
                input = nlsp.check_even(input)
                output = nlsp.change_length_signal(output,len(input))
                filterk, nl = nlsp.adaptive_identification(input,output,branches=branches)
                file_name = ''.join([file_name,'Adaptive'])
                filterk = sumpf.modules.MergeSignals(signals=filterk).GetOutput()
                sumpf.modules.SignalFile(filename=file_name,signal=filterk,format=sumpf.modules.SignalFile.NUMPY_NPZ)
            elif code is 'LogeshSweep': # sweep based system identification
                input = nlsp.NovakSweepGenerator_Sine(sampling_rate=44100,length=2**18,start_frequency=20.0,
                                                      stop_frequency=20000.0,fade_out=0.00,fade_in=0.00)
                output = sumpf.modules.SignalFile(filename=response,format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
                output = sumpf.modules.SplitSignal(data=output,channels=[0]).GetOutput()
                output = nlsp.change_length_signal(output,len(input.GetOutput()))
                output = sumpf.modules.ShiftSignal(signal=output,shift=1000,circular=False).GetOutput()
                filterk, nl = nlsp.sine_sweepbased_temporalreversal(input,output,branches=branches)
                file_name = ''.join([file_name,'SineSweep'])
                filterk = sumpf.modules.MergeSignals(signals=filterk).GetOutput()
                sumpf.modules.SignalFile(filename=file_name,signal=filterk,format=sumpf.modules.SignalFile.NUMPY_NPZ)
                # Linear system identification
                input = nlsp.NovakSweepGenerator_Sine(sampling_rate=44100,length=2**18,start_frequency=20.0,
                                                      stop_frequency=20000.0,fade_out=0.00,fade_in=0.00)
                output = sumpf.modules.SignalFile(filename=response,format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
                output = sumpf.modules.SplitSignal(data=output,channels=[0]).GetOutput()
                output = nlsp.change_length_signal(output,len(input.GetOutput()))
                output = sumpf.modules.ShiftSignal(signal=output,shift=1000,circular=False).GetOutput()
                filterk, nl = nlsp.linear_identification(input,output,branches=branches)
                file_name = ''.join([file_name,'Linear'])
                filterk = sumpf.modules.MergeSignals(signals=filterk).GetOutput()
                sumpf.modules.SignalFile(filename=file_name,signal=filterk,format=sumpf.modules.SignalFile.NUMPY_NPZ)


# Test the model using samples
# 1. Read the input and output files
# 2. Match input and output
# 3. Find the system which produces the output
# 5. Retrieve the model of the system
# 6. Find the accuracy of the system identification

def read_inputs():
    src = os.path.join(source_directory,"Inputs")
    input_path = os.path.join(src,"Input")
    output_path = os.path.join(src,"Output")
    input_files = os.listdir(input_path)
    output_files = os.listdir(output_path)
    input_files_club = []
    output_files_club = []
    for outputs in output_files:
        name = outputs.split('_')[2]
        output_file = os.path.join(output_path,outputs)
        for inputs in input_files:
            if name in inputs:
                input_file = os.path.join(input_path,inputs)
        input_files_club.append(input_file)
        output_files_club.append(output_file)
    inputs = zip(input_files_club, output_files_club)
    return inputs

def construct_models():
    model_path = os.path.join(source_directory,"Models")
    car_names = []
    constructed_models = []
    Method_name = []
    for model_kernel in os.listdir(model_path):
        filter_kernels = sumpf.modules.SignalFile(filename=os.path.join(model_path,model_kernel),
                                 format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
        spec = sumpf.modules.FourierTransform(filter_kernels).GetSpectrum()
        filter_kernels = nlsp.multichanneltoarray(filter_kernels)
        car_name = model_kernel.split('_')[0]
        if 'SineSweep' in model_kernel:
            method = 'SineSweep'
            nl_functions = nlsp.nl_branches(nlsp.function_factory.power_series,branches=branches)
        elif 'Adaptive' in model_kernel:
            method = 'Adaptive'
            nl_functions = nlsp.nl_branches(nlsp.function_factory.laguerre_polynomial,branches=branches)
        elif 'Linear' in model_kernel:
            method = 'Linear'
            nl_functions = nlsp.nl_branches(nlsp.function_factory.power_series,branches=branches)
        filter_kernels = nlsp.change_length_filterkernels(filter_kernels=filter_kernels,length=2**11)
        model_constructed = nlsp.HammersteinGroupModel_up(input_signal=sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=44100,length=2**10).GetSignal(),
                                                          nonlinear_functions=nl_functions,
                                                          filter_irs=filter_kernels,max_harmonics=range(1,branches+1))
        car_names.append(car_name)
        constructed_models.append(model_constructed)
        Method_name.append(method)
    Models = zip(car_names,constructed_models,Method_name)
    return Models

def check_accuracy(models, inputs):
    for input,output in inputs:
        inp_signal = sumpf.modules.SignalFile(filename=input,format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
        out_signal = sumpf.modules.SignalFile(filename=output,format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
        inp_signal = sumpf.modules.CutSignal(signal=inp_signal,stop=2**16).GetOutput()
        out_signal = sumpf.modules.CutSignal(signal=out_signal,stop=2**16).GetOutput()
        for car_name, model, method in models:
            if car_name in output:
                model.SetInput(inp_signal)
                model_output = model.GetOutput()
                system_output = out_signal
                system_output = sumpf.modules.SplitSignal(data=system_output, channels=[0]).GetOutput()
                print method
                print output
                print nlsp.snr(system_output,model_output)
                del system_output
                del model_output
        del inp_signal
        del out_signal


def main():
    system_identification_algorithm(read_excitations())
    check_accuracy(models=construct_models(),inputs=read_inputs())


main()