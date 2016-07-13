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
    output_path = "C:/Users/diplomand.8/Desktop/Thomas_arbeit/Test_selection/"


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

analyze_nonlinearity()