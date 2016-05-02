import sumpf
import nlsp
import nlsp.common.plots as plot


def adaptive_initializedwith_sweepidentification():
    # generate virtual nonlinear system using HGM
    ref_nlsystem = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind_noise,
                                                 max_harmonics=range(1,branches+1))

    # give input and get output from the virtual nlsystem
    ref_nlsystem.SetInput(input)
    output_noise = ref_nlsystem.GetOutput()
    input_noise = input
    ref_nlsystem.SetInput(sine_g.GetOutput())
    output_sine = ref_nlsystem.GetOutput()
    ref_nlsystem.SetInput(cos_g.GetOutput())
    output_cos = ref_nlsystem.GetOutput()

    # only sine based system identification
    found_filter_spec_sine, nl_function_sine = nlsp.systemidentification("powerhgmbp1",nlsp.nonlinearconvolution_powerseries_temporalreversal,
                                                                         branches,sine_g,output_sine)
    iden_nlsystem_sine = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sine,
                                                  filter_irs=found_filter_spec_sine)

    # only cosine based system identification
    found_filter_spec_cos, nl_function_cos = nlsp.systemidentification("powerhgmbp1",nlsp.nonlinearconvolution_chebyshev_temporalreversal,
                                                                         branches,cos_g,output_cos)
    iden_nlsystem_cos = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cos,
                                                  filter_irs=found_filter_spec_cos)

    # only noise based system identification
    found_filter_spec_adapt, nl_function_adapt = nlsp.systemidentification("powerhgmbp1",nlsp.adaptive_identification_hermite,
                                                                           branches,wgn_normal_g,output_noise)
    iden_nlsystem_adapt = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_adapt,
                                                  filter_irs=found_filter_spec_adapt)

    # sine based as init coeff for noise based system identification
    found_filter_spec_sine_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_sine,length=filter_taps)
    found_filter_spec_sineadapt_power, nl_function_sineadapt_power = nlsp.adaptive_identification_powerseries(input_generator=input_noise,outputs=output_noise,iterations=i,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength,Print=True)
    found_filter_spec_sineadapt_hermite, nl_function_sineadapt_hermite = nlsp.adaptive_identification_hermite(input_generator=input_noise,outputs=output_noise,iterations=i,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength,Print=True)
    found_filter_spec_sineadapt_legendre, nl_function_sineadapt_legendre = nlsp.adaptive_identification_legendre(input_generator=input_noise,outputs=output_noise,iterations=i,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength,Print=True)
    found_filter_spec_sineadapt_cheby, nl_function_sineadapt_cheby = nlsp.adaptive_identification_chebyshev(input_generator=input_noise,outputs=output_noise,iterations=i,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_sine_reducedlength,Print=True)
    iden_nlsystem_sineadapt_power = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sineadapt_power,
                                                  filter_irs=found_filter_spec_sineadapt_power)
    iden_nlsystem_sineadapt_cheby = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sineadapt_cheby,
                                                  filter_irs=found_filter_spec_sineadapt_cheby)
    iden_nlsystem_sineadapt_hermite = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sineadapt_hermite,
                                                  filter_irs=found_filter_spec_sineadapt_hermite)
    iden_nlsystem_sineadapt_legendre = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_sineadapt_legendre,
                                                  filter_irs=found_filter_spec_sineadapt_legendre)

    # cos based as init coeff for noise based system identification
    found_filter_spec_cos_reducedlength = nlsp.change_length_filterkernels(found_filter_spec_cos,length=filter_taps)
    found_filter_spec_cosadapt_cheby, nl_function_cosadapt_cheby = nlsp.adaptive_identification_chebyshev(input_generator=input_noise,outputs=output_noise,iterations=i,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,Print=True)
    found_filter_spec_cosadapt_power, nl_function_cosadapt_power = nlsp.adaptive_identification_powerseries(input_generator=input_noise,outputs=output_noise,iterations=i,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,Print=True)
    found_filter_spec_cosadapt_legendre, nl_function_cosadapt_legendre = nlsp.adaptive_identification_legendre(input_generator=input_noise,outputs=output_noise,iterations=i,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,Print=True)
    found_filter_spec_cosadapt_hermite, nl_function_cosadapt_hermite = nlsp.adaptive_identification_hermite(input_generator=input_noise,outputs=output_noise,iterations=i,branches=branches,
                                                                   step_size=0.1,filtertaps=filter_taps,algorithm=nlsp.multichannel_nlms,Plot=False,init_coeffs=found_filter_spec_cos_reducedlength,Print=True)

    iden_nlsystem_cosadapt_cheby = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cosadapt_cheby,
                                                  filter_irs=found_filter_spec_cosadapt_cheby)
    iden_nlsystem_cosadapt_power = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cosadapt_power,
                                                  filter_irs=found_filter_spec_cosadapt_power)
    iden_nlsystem_cosadapt_hermite = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cosadapt_hermite,
                                                  filter_irs=found_filter_spec_cosadapt_hermite)
    iden_nlsystem_cosadapt_legendre = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_cosadapt_legendre,
                                                  filter_irs=found_filter_spec_cosadapt_legendre)


    # set reference input to virtual nlsystem and identified nl system
    ref_nlsystem.SetInput(reference)
    iden_nlsystem_sine.SetInput(reference)
    iden_nlsystem_cos.SetInput(reference)
    iden_nlsystem_adapt.SetInput(reference)
    iden_nlsystem_sineadapt_power.SetInput(reference)
    iden_nlsystem_sineadapt_cheby.SetInput(reference)
    iden_nlsystem_sineadapt_legendre.SetInput(reference)
    iden_nlsystem_sineadapt_hermite.SetInput(reference)
    iden_nlsystem_cosadapt_power.SetInput(reference)
    iden_nlsystem_cosadapt_cheby.SetInput(reference)
    iden_nlsystem_cosadapt_legendre.SetInput(reference)
    iden_nlsystem_cosadapt_hermite.SetInput(reference)

    # calculate snr value
    powerseries_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_sine.GetOutput())
    chebyshev_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_cos.GetOutput())
    adaptive_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_adapt.GetOutput())
    adaptivesine_power_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_sineadapt_power.GetOutput())
    adaptivesine_cheby_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_sineadapt_cheby.GetOutput())
    adaptivesine_hermite_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_sineadapt_hermite.GetOutput())
    adaptivesine_legendre_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_sineadapt_legendre.GetOutput())
    adaptivecos_power_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_cosadapt_power.GetOutput())
    adaptivecos_cheby_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_cosadapt_cheby.GetOutput())
    adaptivecos_legendre_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_cosadapt_legendre.GetOutput())
    adaptivecos_hermite_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_cosadapt_hermite.GetOutput())

    # print snr value
    print "SNR of powerseries nl convolution: %r" %powerseries_snr
    print "SNR of chebyshev nl convolution: %r" %chebyshev_snr
    print "SNR of adaptive: %r" %adaptive_snr
    print "SNR of adaptive sine power: %r" %adaptivesine_power_snr
    print "SNR of adaptive sine cheby: %r" %adaptivesine_cheby_snr
    print "SNR of adaptive sine hermite: %r" %adaptivesine_hermite_snr
    print "SNR of adaptive sine legendre: %r" %adaptivesine_legendre_snr
    print "SNR of adaptive cos power: %r" %adaptivecos_power_snr
    print "SNR of adaptive cos cheby: %r" %adaptivecos_cheby_snr
    print "SNR of adaptive cos legendre: %r" %adaptivecos_legendre_snr
    print "SNR of adaptive cos hermite: %r" %adaptivecos_hermite_snr

def adaptive_differentnlfunctions():
    # generate virtual nonlinear system using HGM
    ref_nlsystem = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind_noise,
                                                 max_harmonics=range(1,branches+1))

    # give input and get output from the virtual nlsystem
    ref_nlsystem.SetInput(input)
    output_noise = ref_nlsystem.GetOutput()
    input_noise = input

    # only noise based system identification
    found_filter_spec_adapt_power, nl_function_adapt_power = nlsp.adaptive_identification_powerseries(input_generator=input_noise,outputs=output_noise,
                                                                                                      branches=branches,iterations=i,filtertaps=filter_taps,Print=True)
    found_filter_spec_adapt_cheby, nl_function_adapt_cheby = nlsp.adaptive_identification_chebyshev(input_generator=input_noise,outputs=output_noise,
                                                                                                      branches=branches,iterations=i,filtertaps=filter_taps,Print=True)
    found_filter_spec_adapt_hermite, nl_function_adapt_hermite = nlsp.adaptive_identification_hermite(input_generator=input_noise,outputs=output_noise,
                                                                                                      branches=branches,iterations=i,filtertaps=filter_taps,Print=True)
    found_filter_spec_adapt_legendre, nl_function_adapt_legendre = nlsp.adaptive_identification_legendre(input_generator=input_noise,outputs=output_noise,
                                                                                                      branches=branches,iterations=i,filtertaps=filter_taps,Print=True)

    iden_nlsystem_adapt_power = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_adapt_power,
                                                  filter_irs=found_filter_spec_adapt_power)
    iden_nlsystem_adapt_cheby = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_adapt_cheby,
                                                  filter_irs=found_filter_spec_adapt_cheby)
    iden_nlsystem_adapt_hermite = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_adapt_hermite,
                                                  filter_irs=found_filter_spec_adapt_hermite)
    iden_nlsystem_adapt_legendre = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_adapt_legendre,
                                                  filter_irs=found_filter_spec_adapt_legendre)


    # set reference input to virtual nlsystem and identified nl system
    ref_nlsystem.SetInput(reference)
    iden_nlsystem_adapt_power.SetInput(reference)
    iden_nlsystem_adapt_cheby.SetInput(reference)
    iden_nlsystem_adapt_hermite.SetInput(reference)
    iden_nlsystem_adapt_legendre.SetInput(reference)

    # calculate snr value
    adaptive_powerseries_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_adapt_power.GetOutput())
    adaptive_chebyshev_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_adapt_cheby.GetOutput())
    adaptive_hermite_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_adapt_hermite.GetOutput())
    adaptive_legendre_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_adapt_legendre.GetOutput())

    # print snr value
    print "adaptive_powerseries_snr: %r" %adaptive_powerseries_snr
    print "adaptive_chebyshev_snr: %r" %adaptive_chebyshev_snr
    print "adaptive_hermite_snr: %r" %adaptive_hermite_snr
    print "adaptive_legendre_snr: %r" %adaptive_legendre_snr

def adaptive_differentlengthanditerations():
    # generate virtual nonlinear system using HGM
    ref_nlsystem = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                                 filter_irs=filter_spec_tofind_noise,
                                                 max_harmonics=range(1,branches+1))

    # give input and get output from the virtual nlsystem
    ref_nlsystem.SetInput(input)
    output_noise = ref_nlsystem.GetOutput()
    input_noise = input

    # only noise based system identification
    found_filter_spec_adapt_hermite, nl_function_adapt_hermite = nlsp.adaptive_identification_hermite(input_generator=input_noise,outputs=output_noise,
                                                                                                      branches=branches,iterations=i,filtertaps=filter_taps,Print=True)

    iden_nlsystem_adapt_hermite = nlsp.HammersteinGroupModel_up(max_harmonics=range(1,branches+1),nonlinear_functions=nl_function_adapt_hermite,
                                                  filter_irs=found_filter_spec_adapt_hermite)


    # set reference input to virtual nlsystem and identified nl system
    ref_nlsystem.SetInput(reference)
    iden_nlsystem_adapt_hermite.SetInput(reference)

    # calculate snr value
    adaptive_hermite_snr = nlsp.snr(ref_nlsystem.GetOutput(),iden_nlsystem_adapt_hermite.GetOutput())

    # print snr value
    print "adaptive_hermite_snr: %r" %adaptive_hermite_snr

sampling_rate = 48000.0
start_freq = 20.0
stop_freq = 20000.0
length = 2**15
fade_out = 0.00
fade_in = 0.00
filter_taps = 2**10
branches = 3
normal = sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0,standard_deviation=1.0)
uniform = sumpf.modules.NoiseGenerator.UniformDistribution()
laplace = sumpf.modules.NoiseGenerator.LaplaceDistribution()

Plot = True
Save = False

sine_g = nlsp.NovakSweepGenerator_Sine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
cos_g = nlsp.NovakSweepGenerator_Cosine(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, fade_out= fade_out,fade_in=fade_in)
wgn_normal_g = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=normal)
wgn_uniform_g = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=uniform)
wgn_laplace_g = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=laplace)
reference = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=length, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=sumpf.modules.NoiseGenerator.LaplaceDistribution())
reference = sumpf.modules.ClipSignal(reference.GetOutput()).GetOutput()
input = wgn_normal_g.GetOutput()
filter_spec_tofind_noise = nlsp.log_bpfilter(branches=branches,input=input)
i = 5
###################################################################
# adaptive_initializedwith_sweepidentification()

##################################################################
# inputg = [wgn_normal_g,wgn_uniform_g,wgn_laplace_g]
# for input in inputg:
#     input = input.GetOutput()
#     adaptive_differentnlfunctions()

##################################################################
# reference = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=2**18, start_frequency=start_freq,
#                                    stop_frequency=stop_freq, distribution=sumpf.modules.NoiseGenerator.LaplaceDistribution())
# reference = sumpf.modules.ClipSignal(reference.GetOutput()).GetOutput()
#
# adaptive_differentlengthanditerations()
##################################################################
reference = nlsp.WhiteGaussianGenerator(sampling_rate=sampling_rate, length=2**18, start_frequency=start_freq,
                                   stop_frequency=stop_freq, distribution=sumpf.modules.NoiseGenerator.LaplaceDistribution())
reference = sumpf.modules.ClipSignal(reference.GetOutput()).GetOutput()
for i in range(1,6):
    adaptive_differentlengthanditerations()