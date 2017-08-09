import sumpf
import nlsp
import nlsp.common.plots as plot

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**16
fade_out = 0.00
fade_in = 0.00
branches = 3
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
              sine,
              sine,
              cos,
              wgn_uniform,
              wgn_normal,
              wgn_normal]
iden_method = [nlsp.linear_identification,
               nlsp.linear_identification_powerhgm,
               nlsp.sine_sweepbased_temporalreversal,
               nlsp.cosine_sweepbased_temporalreversal,
               nlsp.adaptive_identification,
               nlsp.miso_identification,
               nlsp.wiener_g_identification]
nonlinear_function = [nlsp.function_factory.chebyshev1_polynomial,
                      nlsp.function_factory.chebyshev1_polynomial,
                      nlsp.function_factory.chebyshev1_polynomial,
                      nlsp.function_factory.chebyshev1_polynomial,
                      nlsp.function_factory.chebyshev1_polynomial,
                      nlsp.function_factory.chebyshev1_polynomial,
                      nlsp.function_factory.chebyshev1_polynomial]
reference = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.LaplaceDistribution(mean=0.0,scale=0.2),seed="signal",samplingrate=sampling_rate,length=length).GetSignal()
# reference = sumpf.modules.SweepGenerator(samplingrate=sampling_rate, length=length).GetSignal()
# reference = sumpf.modules.SignalFile(filename="C:/Users/diplomand.8/Desktop/linearHGM_explannation/input_speech",format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
# reference = sumpf.modules.SplitSignal(data=reference, channels=[0]).GetOutput()
reference = nlsp.RemoveOutliers(thresholds=[-1.0,1.0],value=0,signal=reference)
reference = reference.GetOutput()

for method,input_generator,nlfunction in zip(iden_method,excitation,nonlinear_function):
    print method,input_generator
    try:
        nlsp.hgmwithfilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    except:
        print "hgm with filter exception"
nlsp.common.plots.show()
    # try:
    #     nlsp.hgmwithoverlapfilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    # except:
    #     print "hgm with overlap filter exception"
    # try:
    #     nlsp.hgmwithreversedfilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    # except:
    #     print "hgm with reversed filter exception"
    # nlsp.robustness_excitation_evaluation(input_generator,branches,method,Plot,reference)
    # try:
    #     nlsp.robustness_excitation_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "robustness excitation exception"
    # try:
    #     nlsp.robustness_noise_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "robustness noise exception"


    # try:
    #     nlsp.linearmodel_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    # except:
    #     print "linear model exception"
    # try:
    #     nlsp.hgmallpass_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    # except:
    #     print "allpass filter exception"
    # try:
    #     nlsp.hgmwithalphafilter_evaluation(input_generator,branches,nlfunction,method,Plot,reference)
    # except:
    #     print "weighted filtering exception"
    # try:
    #     nlsp.clippingHGMevaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "symmetric clipping HGM exception"
    try:
        nlsp.softclippingHGMevaluation(input_generator,branches,method,Plot,reference)
    except:
        print "symmetric soft clipping HGM exception"
    # try:
    #     nlsp.doublehgm_same_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "double hgm all same exception"
    # try:
    #     nlsp.doublehgm_different_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "double hgm all different exception"
    # try:
    #     nlsp.differentlength_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #    print "different length exception"
    # try:
    #     nlsp.differentbranches_evaluation(input_generator,branches,method,Plot,reference)
    # except:
    #     print "different branches exception"
    #
    #
    #

# nlsp.adaptive_identification()

for method,input_generator in zip(iden_method,excitation):
    print method,input_generator
    try:
        nlsp.computationtime_evaluation(input_generator,branches,method,Plot,rangevalue=5,save=False)
    except:
        print "computation time evaluation exception"
# try:
#     nlsp.computationtime_adaptive_evaluation(wgn_uniform,branches)
# except:
#     print "adaptive identification computation time evaluation exception"

nlsp.save_systemidentification()


