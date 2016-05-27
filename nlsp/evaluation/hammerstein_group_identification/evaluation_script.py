import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**15
fade_out = 0.00
fade_in = 0.00
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

excitation = [sine,
              cos,
              wgn_normal,
              wgn_normal,
              wgn_normal,
              wgn_uniform,]
iden_method = [nlsp.nonlinearconvolution_powerseries_temporalreversal,
               nlsp.nonlinearconvolution_chebyshev_temporalreversal,
               nlsp.adaptive_identification_powerseries,
               nlsp.adaptive_identification_hermite,
               nlsp.miso_identification,
               nlsp.wiener_g_identification_corr]
reference = nlsp.RemoveOutliers(thresholds=[-1.0,1.0],value=0,signal=wgn_laplace.GetOutput())
reference = reference.GetOutput()

for method,input_generator in zip(iden_method,excitation):
    print method,input_generator
    # try:
    #     nlsp.hgmwithfilter_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "hgm with filter exception"
    # try:
    #     nlsp.hgmwithoverlapfilter_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "hgm with overlap filter exception"
    # try:
    #     nlsp.linearmodel_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "linear model exception"
    # try:
    #     nlsp.hgmwithreversedfilter_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "hgm with reversed filter exception"
    # try:
    #     nlsp.hgmwithamplifiedfilter_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "amplified filter exception"
    # try:
    #     nlsp.hgmallpass_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "allpass filter exception"
    # try:
    #     nlsp.puretone_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "puretone exception"
    # try:
    #     nlsp.hgmwithalphafilter_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "weighted filtering exception"


    try:
        nlsp.clippingHGMevaluation(input_generator,branches,method,Plot,reference)
    except:
        print "symmetric clipping HGM exception"
    try:
        nlsp.softclippingHGMevaluation(input_generator,branches,method,Plot,reference)
    except:
        print "symmetric soft clipping HGM exception"
    # try:
    #     nlsp.symmetric_hardclipping_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "symmetric hardclipping exception"
    # try:
    #     nlsp.nonsymmetric_hardclipping_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "nonsymmetric hardclipping exception"
    # try:
    #     nlsp.softclipping_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "soft clipping exception"
    # try:
    #     nlsp.doublehgm_same_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "double hgm all same exception"
    # try:
    #     nlsp.doublehgm_different_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "double hgm all different exception"
    # try:
    #     nlsp.doublehgm_samefilter_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "double hgm same filter exception"
    # try:
    #     nlsp.doublehgm_samenl_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "double hgm same nl exception"





    # try:
    #     nlsp.differentlength_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #    print "different length exception"
    # try:
    #     nlsp.differentbranches_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "different branches exception"
    # try:
    #     nlsp.robustness_excitation_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "robustness excitation exception"
    # try:
    #     nlsp.robustness_noise_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "robustness noise exception"
    # try:
    #     nlsp.robustness_differentexcitation_evaluation(input_generator,branches,method,Plot)
    # except:
    #     print "robustness different noise excitation exception"


# for method,input_generator in zip(iden_method,excitation):
#     print method,input_generator
#     try:
#         nlsp.computationtime_evaluation(input_generator,branches,method,Plot,rangevalue=10,save=False)
#     except:
#         print "computation time evaluation exception"
# try:
#     nlsp.computationtime_adaptive_evaluation(wgn_uniform,branches)
# except:
#     print "adaptive identification computation time evaluation exception"


