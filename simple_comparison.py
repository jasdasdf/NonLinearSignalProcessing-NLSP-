import os
import sumpf
import nlsp


def car_ls_modeling():

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

car_ls_modeling()