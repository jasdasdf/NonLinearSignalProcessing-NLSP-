# Modeling interior acoustics of a car

import os
import sumpf
import nlsp

def get_sweep_generator():
    sampling_rate = 44100
    length = 2**18
    start_frequency = 20.0
    stop_frequency = 20000.0
    fade_in = 0.0
    fade_out = 0.0
    input_sweep_gen = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_frequency,
                                  stop_frequency=stop_frequency, fade_in=fade_in, fade_out=fade_out)
    return input_sweep_gen


def car_ls_modeling_sweep():

    # input sweep parameters
    sampling_rate = 44100
    length = 2**18
    start_frequency = 20.0
    stop_frequency = 20000.0
    fade_in = 0.0
    fade_out = 0.0
    channel = 0
    branches = 3
    output_path = "C:/Users/diplomand.8/Desktop/Thomas_arbeit/Test_selection/temp/"
    iden_method = nlsp.sine_sweepbased_temporalreversal


    input_sweep_gen = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_frequency,
                                  stop_frequency=stop_frequency, fade_in=fade_in, fade_out=fade_out)
    output_listdir = os.listdir(output_path)
    for file in output_listdir:
        file_output = os.path.join(output_path, file)
        print file_output
        load_output = sumpf.modules.SignalFile(filename=file_output, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
        load_output = sumpf.modules.SplitSignal(data=load_output, channels=[channel]).GetOutput()
        # print len(load_output),len(input_sweep_gen.GetOutput())
        load_output = nlsp.change_length_signal(load_output,len(input_sweep_gen.GetOutput()))
        sweep_output = load_output
        sweep_output = sumpf.modules.ShiftSignal(signal=sweep_output, shift=1000, circular=False).GetOutput()
        found_filter_spec, nl_functions = iden_method(input_sweep_gen,sweep_output,branches)
        model = nlsp.HammersteinGroupModel_up(input_signal=input_sweep_gen.GetOutput(),
                                                     nonlinear_functions=nl_functions,
                                                     filter_irs=found_filter_spec,
                                                     max_harmonics=range(1,branches+1))
        found_filter_spec_linear, nl_functions_linear = nlsp.linear_identification(input_sweep_gen,sweep_output,branches)
        linear_model = nlsp.HammersteinGroupModel_up(input_signal=input_sweep_gen.GetOutput(),
                                             nonlinear_functions=nl_functions_linear,
                                             filter_irs=found_filter_spec_linear)
        model.SetInput(input_sweep_gen.GetOutput())
        linear_model.SetInput(input_sweep_gen.GetOutput())
        nlsp.common.plots.plot(sumpf.modules.FourierTransform(sweep_output).GetSpectrum(),show=False)
        nlsp.common.plots.plot(sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),show=False)
        nlsp.common.plots.plot(sumpf.modules.FourierTransform(linear_model.GetOutput()).GetSpectrum(),show=True)
        snr = nlsp.snr(sweep_output,model.GetOutput())
        snr_linear = nlsp.snr(sweep_output,linear_model.GetOutput())
        print "Nonlinear model SNR:%r, Linear model SNR:%r" %(snr,snr_linear)

def car_ls_modeling_online(excitation, response, input, output, branches, algorithm):
    # load all signals
    input = sumpf.modules.SignalFile(filename=input, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
    output = sumpf.modules.SignalFile(filename=output, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
    excitation = sumpf.modules.SignalFile(filename=excitation, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
    response = sumpf.modules.SignalFile(filename=response, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
    input = sumpf.modules.SplitSignal(data=input, channels=[0]).GetOutput()
    output = sumpf.modules.SplitSignal(data=output, channels=[0]).GetOutput()
    excitation = sumpf.modules.SplitSignal(data=excitation, channels=[0]).GetOutput()
    response = sumpf.modules.SplitSignal(data=response, channels=[0]).GetOutput()
    output = sumpf.modules.ShiftSignal(signal=output, shift=1000, circular=False).GetOutput()
    excitation = nlsp.change_length_signal(excitation,length=len(excitation)-1)
    response = nlsp.change_length_signal(response,length=len(excitation))
    input = nlsp.change_length_signal(input,length=len(excitation))
    output = nlsp.change_length_signal(output,length=len(input))
    print len(input),len(excitation),len(response),len(output)

    # system identification
    found_filter_spec, nl_functions = algorithm(excitation,response,branches)
    model = nlsp.HammersteinGroupModel_up(input_signal=excitation,
                                                 nonlinear_functions=nl_functions,
                                                 filter_irs=found_filter_spec,
                                                 max_harmonics=range(1,branches+1))
    found_filter_spec_linear, nl_functions_linear = nlsp.adaptive_identification(excitation,response,branches=1)
    linear_model = nlsp.HammersteinGroupModel_up(input_signal=excitation,
                                         nonlinear_functions=nl_functions_linear,
                                         filter_irs=found_filter_spec_linear)

    # excitation modeling accuracy
    model.SetInput(excitation)
    linear_model.SetInput(excitation)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(response).GetSpectrum(),show=False)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),show=False)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(linear_model.GetOutput()).GetSpectrum(),show=True)
    snr = nlsp.snr(response,model.GetOutput())
    snr_linear = nlsp.snr(response,linear_model.GetOutput())
    print "Nonlinear model SNR (Excitation):%r, Linear model SNR (Excitation):%r" %(snr,snr_linear)

    # sample modeling accuracy
    model.SetInput(input)
    linear_model.SetInput(input)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(output).GetSpectrum(),show=False)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),show=False)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(linear_model.GetOutput()).GetSpectrum(),show=True)
    snr = nlsp.snr(output,model.GetOutput())
    snr_linear = nlsp.snr(output,linear_model.GetOutput())
    print "Nonlinear model SNR (Sample):%r, Linear model SNR (Sample):%r" %(snr,snr_linear)

def save_model_car(excitation_location, response_location, iden_method, locationandname):

    # process excitation and response files
    excitation = sumpf.modules.SignalFile(filename=excitation_location, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
    response = sumpf.modules.SignalFile(filename=response_location, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
    excitation = sumpf.modules.SplitSignal(data=excitation, channels=[0]).GetOutput()
    response = sumpf.modules.SplitSignal(data=response, channels=[0]).GetOutput()
    response = sumpf.modules.ShiftSignal(signal=response, shift=1000, circular=False).GetOutput()
    response = nlsp.change_length_signal(response,length=len(excitation))

    # system identification
    found_filter_spec, nl_functions = algorithm(excitation,response,branches)
    model = nlsp.HammersteinGroupModel_up(nonlinear_functions=nl_functions,
                                          filter_irs=found_filter_spec,
                                          max_harmonics=range(1,branches+1))
    nlsp.save_systemidentification(method=iden_method, filterkernels=found_filter_spec, nonlinearfunc="")

    # excitation modeling accuracy
    model.SetInput(excitation)
    linear_model.SetInput(excitation)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(response).GetSpectrum(),show=False)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(model.GetOutput()).GetSpectrum(),show=False)
    nlsp.common.plots.plot(sumpf.modules.FourierTransform(linear_model.GetOutput()).GetSpectrum(),show=True)
    snr = nlsp.snr(response,model.GetOutput())
    snr_linear = nlsp.snr(response,linear_model.GetOutput())
    print "Nonlinear model SNR (Excitation):%r, Linear model SNR (Excitation):%r" %(snr,snr_linear)

excitation = "C:/Users/diplomand.8/Desktop/Database_nlsp/24_MLS_O16_R05_LR.wav"
response = "C:/Users/diplomand.8/Desktop/Database_nlsp/Skoda/Skoda Superb AC HA 3600_24_MLS_O16_R05_LR_DF_70dBA.wav"
input = "C:/Users/diplomand.8/Desktop/Database_nlsp/Raw/Raw_04_No One Else_LIN_nominal.wav"
output = "C:/Users/diplomand.8/Desktop/Database_nlsp/Skoda/Skoda Superb AC HA 3600_04_No One Else_DF_70dBA.wav"
branches = 5
algorithm = nlsp.adaptive_identification
car_ls_modeling_online(excitation,response,input,output,branches,algorithm)

# car_ls_modeling_sweep()