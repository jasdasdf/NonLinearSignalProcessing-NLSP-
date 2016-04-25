import nlsp
import sumpf


def getnl_ir(sweep_generator,output_sweep,branches=5):
    sweep_length = sweep_generator.GetLength()
    sweep_start_freq = sweep_generator.GetStartFrequency()
    sweep_stop_freq = sweep_generator.GetStopFrequency()
    ip_signal = sweep_generator.GetOutput()

    # output_sweep = nlsp.append_zeros(output_sweep)
    rev = sweep_generator.GetReversedOutput()
    rev_spec = sumpf.modules.FourierTransform(rev).GetSpectrum()
    out_spec = sumpf.modules.FourierTransform(output_sweep).GetSpectrum()
    out_spec = out_spec / output_sweep.GetSamplingRate()
    tf = rev_spec * out_spec
    ir_sweep = sumpf.modules.InverseFourierTransform(tf).GetSignal()
    # nlsp.common.plots.plot(ir_sweep)

    ir_sweep_direct = sumpf.modules.CutSignal(signal=ir_sweep,start=0,stop=int(sweep_length/4)).GetOutput()
    ir_sweep_direct = nlsp.append_zeros(ir_sweep_direct)
    ir_merger = sumpf.modules.MergeSignals(on_length_conflict=sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
    ir_merger.AddInput(ir_sweep_direct)
    for i in range(branches-1):
        split_harm = nlsp.FindHarmonicImpulseResponse_Novak(impulse_response=ir_sweep,
                                                            harmonic_order=i+2,
                                                            sweep_generator=sweep_generator).GetHarmonicImpulseResponse()
        split_harm = sumpf.modules.CutSignal(signal=split_harm,stop=len(sweep_generator.GetOutput())).GetOutput()
        ir_merger.AddInput(sumpf.Signal(channels=split_harm.GetChannels(),
                                        samplingrate=ir_sweep.GetSamplingRate(), labels=split_harm.GetLabels()))
    ir_merger = ir_merger.GetOutput()

    # nlsp.common.plots.plot(ir_merger)
    return ir_sweep