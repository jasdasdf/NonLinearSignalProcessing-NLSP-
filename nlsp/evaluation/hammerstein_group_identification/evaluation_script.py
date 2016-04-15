import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000.0
start_freq = 100.0
stop_freq = 20000.0
length = 2**16
fade_out = 0.00
fade_in = 0.00
branches = 5
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()

Plot = False
Save = False

sine = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
cos = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
wgn_normal = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
wgn_uniform = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)
excitation = [sine,
              cos,
              wgn_normal,
              wgn_uniform,
              wgn_normal]
iden_method = [nlsp.nonlinearconvolution_powerseries_temporalreversal,
               nlsp.nonlinearconvolution_chebyshev_temporalreversal,
               nlsp.miso_identification,
               nlsp.wiener_g_identification_corr,
               nlsp.adaptive_identification]
labels = ["NL_powerseries","NL_chebyshev","MISO","WienerG","adaptive"]

for method,input_generator,label in zip(iden_method,excitation,labels):
    print method,input_generator

    # accuracy evaluation

    nlsp.hgmwithfilter_evaluation(input_generator,branches,method,Plot,label)
    nlsp.hgmwithoverlapfilter_evaluation(input_generator,branches,method,Plot)
    nlsp.linearmodel_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmwithreversedfilter_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmwithamplifiedfilter_evaluation(input_generator,branches,method,Plot)
    nlsp.hgmallpass_evaluation(input_generator,branches,method,Plot)
    nlsp.puretone_evaluation(input_generator,branches,method,Plot)

    nlsp.hardclipping_evaluation(input_generator,branches,method,Plot)
    nlsp.softclipping_evaluation(input_generator,branches,method,Plot)
    nlsp.doublehgm_same_evaluation(input_generator,branches,method,Plot)

    # performance evaluation

    nlsp.differentlength_evaluation(input_generator,branches,method,Plot)
    nlsp.differentbranches_evaluation(input_generator,branches,method,Plot)
    nlsp.computationtime_evaluation(input_generator,branches,method,Plot)

    # robustness evaluation

    nlsp.robustness_excitation_evaluation(input_generator,branches,method,Plot)
    nlsp.robustness_noise_evaluation(input_generator,branches,method,Plot)
plot.show()