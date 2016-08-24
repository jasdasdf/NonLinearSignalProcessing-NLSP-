import os
import sumpf
import nlsp

def analyze_nonlinearity():

    # input sweep parameters
    sampling_rate = 44100
    length = 2**18
    start_frequency = 20.0
    stop_frequency = 20000.0
    fade_in = 0.0
    fade_out = 0.0
    channel = 0
    output_path = "C:/Users/diplomand.8/Desktop/Thomas_arbeit/Test_selection/for_IR/"


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
        nlsp.common.plots.plot(sumpf.modules.FourierTransform(sweep_output).GetSpectrum())
        nl_ir = nlsp.get_nl_impulse_response(input_sweep_gen, sweep_output)
        # nlsp.common.plots.plot(nl_ir)
        direct = sumpf.modules.CutSignal(nl_ir,stop=int(length*0.3)).GetOutput()
        harmonics = sumpf.modules.CutSignal(nl_ir,start=int(length*0.7)).GetOutput()
        # harm_energy = nlsp.calculateenergy_time(harmonics)
        # linear_energy = nlsp.calculateenergy_time(direct)
        harm_energy = nlsp.exponential_energy(harmonics)
        linear_energy = nlsp.exponential_energy(direct)
        # ratio = harm_energy[0] / (linear_energy[0] + harm_energy[0])
        ratio = harm_energy[0] / (linear_energy[0])
        print "Distortion parameter %r" %(ratio*100)
        print
# analyze_nonlinearity()


def get_impulseresponse():
    sampling_rate = 44100
    length = 2**18
    start_frequency = 20.0
    stop_frequency = 20000.0
    fade_in = 0.0
    fade_out = 0.0
    cut_length = 1
    input_path = "C:/Users/diplomand.8/Desktop/Thomas_arbeit/Test_selection/for_IR/"
    output_path = "C:/Users/diplomand.8/Desktop/Thomas_arbeit/Test_selection/Impulse_response/"
    input_sweep_gen = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_frequency,
                                  stop_frequency=stop_frequency, fade_in=fade_in, fade_out=fade_out)
    input_files = os.listdir(input_path)
    for input_file in input_files:
        input_file = os.path.join(input_path,input_file)
        input_signal = sumpf.modules.SignalFile(filename=input_file, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
        input_signal = sumpf.modules.CutSignal(signal=input_signal, start=cut_length).GetOutput()
        input_signal_1stchannel = sumpf.modules.SplitSignal(data=input_signal, channels=[0]).GetOutput()
        input_signal_2ndchannel = sumpf.modules.SplitSignal(data=input_signal, channels=[1]).GetOutput()
        input_signal_1stchannel = nlsp.change_length_signal(input_signal_1stchannel, length=len(input_sweep_gen.GetOutput()))
        input_signal_2ndchannel = nlsp.change_length_signal(input_signal_2ndchannel, length=len(input_sweep_gen.GetOutput()))
        impulse_response_1stchannel = nlsp.get_nl_impulse_response(input_sweep_gen, input_signal_1stchannel)
        impulse_response_2ndchannel = nlsp.get_nl_impulse_response(input_sweep_gen, input_signal_2ndchannel)
        cut_ir_1stchannel = sumpf.modules.CutSignal(signal=impulse_response_1stchannel, stop=88200).GetOutput()
        cut_ir_2ndchannel = sumpf.modules.CutSignal(signal=impulse_response_2ndchannel, stop=88200).GetOutput()
        total_ir = sumpf.modules.MergeSignals(signals=[cut_ir_1stchannel,cut_ir_2ndchannel]).GetOutput()
        path, fname = os.path.split(input_file)
        output_file_path = os.path.join(output_path,fname)
        sumpf.modules.SignalFile(filename=output_file_path, signal=total_ir, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()

get_impulseresponse()
