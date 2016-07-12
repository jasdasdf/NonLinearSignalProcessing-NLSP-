import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**15
fade_out = 0.02
fade_in = 0.02
branches = 5
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
pink = sumpf.modules.NoiseGenerator.PinkNoise()
laplace = sumpf.modules.NoiseGenerator.LaplaceDistribution(mean=0.0,scale=0.2)

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
wgn_pink = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=pink)
wgn_laplace = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=laplace)

excitation = [wgn_uniform,]
iden_method = [nlsp.adaptive_identification,]
nonlinear_function = [nlsp.function_factory.power_series,]
reference = nlsp.RemoveOutliers(thresholds=[-1.0,1.0],value=0,signal=wgn_laplace.GetOutput())
reference = reference.GetOutput()


for method,input_generator,nlfunction in zip(iden_method,excitation,nonlinear_function):
    print method,input_generator
    nlsp.hgmwithfilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    try:
        nlsp.hgmwithfilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    except:
        print "hgm with filter exception"
    try:
        nlsp.hgmwithoverlapfilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    except:
        print "hgm with overlap filter exception"
    try:
        nlsp.linearmodel_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    except:
        print "linear model exception"
    try:
        nlsp.hgmwithreversedfilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    except:
        print "hgm with reversed filter exception"
    try:
        nlsp.hgmallpass_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    except:
        print "allpass filter exception"
    try:
        nlsp.hgmwithalphafilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    except:
        print "weighted filtering exception"
    try:
        nlsp.clippingHGMevaluation(input_generator,branches,method,Plot,reference)
    except:
        print "symmetric clipping HGM exception"
    try:
        nlsp.softclippingHGMevaluation(input_generator,branches,method,Plot,reference)
    except:
        print "symmetric soft clipping HGM exception"
    try:
        nlsp.doublehgm_same_evaluation(input_generator,branches,method,Plot,reference)
    except:
        print "double hgm all same exception"
    try:
        nlsp.doublehgm_different_evaluation(input_generator,branches,method,Plot,reference)
    except:
        print "double hgm all different exception"
    try:
        nlsp.differentlength_evaluation(input_generator,branches,method,Plot,reference)
    except:
       print "different length exception"
    try:
        nlsp.differentbranches_evaluation(input_generator,branches,method,Plot,reference)
    except:
        print "different branches exception"



    try:
        nlsp.robustness_excitation_evaluation(input_generator,branches,method,Plot,reference)
    except:
        print "robustness excitation exception"
    try:
        nlsp.robustness_noise_evaluation(input_generator,branches,method,Plot,reference)
    except:
        print "robustness noise exception"


# for method,input_generator in zip(iden_method,excitation):
#     print method,input_generator
#     try:
#         nlsp.computationtime_evaluation(input_generator,branches,method,Plot,rangevalue=5,save=False)
#     except:
#         print "computation time evaluation exception"
# try:
#     nlsp.computationtime_adaptive_evaluation(wgn_uniform,branches)
# except:
#     print "adaptive identification computation time evaluation exception"



