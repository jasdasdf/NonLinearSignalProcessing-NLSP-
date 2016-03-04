import numpy
import itertools
import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000.0
sweep_start_freq = 20.0
sweep_stop_freq = 20000.0
sweep_length = 2**13
branches = 5
distribution = sumpf.modules.NoiseGenerator.GaussianDistribution()
iden_method = [nlsp.wiener_g_identification]

Plot = False
Save = False

wgn = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=sweep_length, start_frequency=sweep_start_freq,
                                   stop_frequency=sweep_stop_freq, distribution=distribution)
excitation = [wgn]

for method,input_generator in zip(iden_method,excitation):
    print method,input_generator
    # nlsp.audio_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmwithfilter_evaluation(input_generator,branches,method,Plot)
    # nlsp.hgmwithoverlapfilter_evaluation(input_generator,branches,method,Plot)
    # nlsp.linearmodel_evaluation(input_generator,branches,method,Plot)
    # nlsp.hgmwithreversedfilter_evaluation(input_generator,branches,method,Plot)
    # nlsp.hgmwithamplifiedfilter_evaluation(input_generator,branches,method,Plot)
    #
    # nlsp.hardclipping_evaluation(input_generator,branches,method,Plot)
    # nlsp.softclipping_evaluation(input_generator,branches,method,Plot)
    # nlsp.doublehgm_same_evaluation(input_generator,branches,method,Plot)
    #
    # nlsp.differentlength_evaluation(input_generator,branches,method,Plot)
    # nlsp.differentbranches_evaluation(input_generator,branches,method,Plot)
    # nlsp.computationtime_evaluation(input_generator,branches,method,Plot)
    #
    # nlsp.robustness_excitation_evaluation(input_generator,branches,method,Plot)
    # nlsp.robustness_noise_evaluation(input_generator,branches,method,Plot)








