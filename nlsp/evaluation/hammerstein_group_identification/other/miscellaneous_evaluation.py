import nlsp
import sumpf
import nlsp.common.plots as plot

def hardvssoft():
    sampling_rate = 48000.0
    start_freq = 20.0
    stop_freq = 20000.0
    length = 2**16
    fade_out = 0.00
    fade_in = 0.00
    sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                       stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
    thresholds = [-1.0,1.0]
    power = 1.0/3.0
    ref_nlsystem_hard_symmetric = sumpf.modules.ClipSignal(thresholds=[-0.7,0.7])
    ref_nlsystem_hard_nonsymmetric = sumpf.modules.ClipSignal(thresholds=[-0.6,0.8])
    ref_nlsystem_soft = nlsp.NLClipSignal(power=power)
    ref_nlsystem_hard_nonsymmetric.SetInput(sine.GetOutput())
    ref_nlsystem_hard_symmetric.SetInput(sine.GetOutput())
    ref_nlsystem_soft.SetInput(sine.GetOutput())

    soft_ir = nlsp.getnl_ir(sine,ref_nlsystem_soft.GetOutput())
    hard_symm_ir = nlsp.getnl_ir(sine,ref_nlsystem_hard_symmetric.GetOutput())
    hard_nonsymm_ir = nlsp.getnl_ir(sine,ref_nlsystem_hard_nonsymmetric.GetOutput())

    # plot.relabelandplot(soft_ir,"soft clipping IR",show=False)
    # plot.relabelandplot(hard_nonsymm_ir,"nonsymmetric hard clipping IR",show=False)
    # plot.relabelandplot(hard_symm_ir,"symmetric hard clipping IR",show=True)

    sine = sumpf.modules.SineWaveGenerator(frequency=1000.0,samplingrate=sampling_rate,length=length)
    ref_nlsystem_hard_nonsymmetric.SetInput(sine.GetSignal())
    ref_nlsystem_hard_symmetric.SetInput(sine.GetSignal())
    ref_nlsystem_soft.SetInput(sine.GetSignal())
    # plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem_soft.GetOutput()).GetSpectrum(),"soft clipping output",show=False)
    plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem_hard_nonsymmetric.GetOutput()).GetSpectrum(),"nonsymmetric hard clipping output",show=False)
    plot.relabelandplot(sumpf.modules.FourierTransform(ref_nlsystem_hard_symmetric.GetOutput()).GetSpectrum(),"symmetric hard clipping output",show=True)


hardvssoft()