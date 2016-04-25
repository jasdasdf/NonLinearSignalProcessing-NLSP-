import numpy
import sumpf
import nlsp
import time
import itertools
import nlsp.common.plots as plot

def computationtime_evaluation(input_generator,branches,iden_method,Plot):

    inputgenerator = input_generator
    branch = reversed(range(2,branches+1))
    length = reversed([2**14,2**15,2**16])

    for branches,signal_length in itertools.product(branch,length):
        sim = []
        iden = []
        for i in range(10):
            inputgenerator.SetLength(signal_length)
            input_signal = inputgenerator.GetOutput()
            filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
            nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
            ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                         nonlinear_functions=nl_func,
                                                         filter_irs=filter_spec_tofind,
                                                         max_harmonics=range(1,branches+1))

            simulation_time_start = time.clock()
            identification_time_start = time.clock()
            found_filter_spec, nl_functions = iden_method(input_generator,ref_nlsystem.GetOutput(),branches)
            identification_time_stop = time.clock()
            iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                         nonlinear_functions=nl_functions,
                                                         filter_irs=found_filter_spec,
                                                         max_harmonics=range(1,branches+1))
            iden_nlsystem.GetOutput()
            simulation_time_stop = time.clock()
            simulation_time = simulation_time_stop - simulation_time_start
            identification_time = identification_time_stop - identification_time_start
            sim.append(simulation_time)
            iden.append(identification_time)

        print "Signal length: %r, branches: %r, simulation time: %r, identification time: %r" %(signal_length,branches,
                                                                                                numpy.average(sim),
                                                                                                numpy.average(iden))
def computationtime_adaptive_evaluation(input_generator, branches):
    identification = [nlsp.adaptive_identification]
    nlfunctions = [nlsp.function_factory.power_series, nlsp.function_factory.chebyshev1_polynomial,
                   nlsp.function_factory.hermite_polynomial, nlsp.function_factory.legrendre_polynomial]
    for identification_alg, nl_function in itertools.product(identification,nlfunctions):
        sim = []
        iden = []
        print identification_alg
        print nl_function
        for i in range(5):
            input_signal = input_generator.GetOutput()
            filter_spec_tofind = nlsp.log_bpfilter(branches=branches,input=input_signal)
            nl_func = nlsp.nl_branches(nlsp.function_factory.power_series,branches)
            ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                         nonlinear_functions=nl_func,
                                                         filter_irs=filter_spec_tofind,
                                                         max_harmonics=range(1,branches+1))
            simulation_time_start = time.clock()
            identification_time_start = time.clock()
            found_filter_spec, nl_functions = identification_alg(input_generator,ref_nlsystem.GetOutput(),branches,nl_function)
            identification_time_stop = time.clock()
            iden_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                                         nonlinear_functions=nl_functions,
                                                         filter_irs=found_filter_spec,
                                                         max_harmonics=range(1,branches+1))
            iden_nlsystem.GetOutput()
            simulation_time_stop = time.clock()
            simulation_time = simulation_time_stop - simulation_time_start
            identification_time = identification_time_stop - identification_time_start
            sim.append(simulation_time)
            iden.append(identification_time)
        print "simulation time: %r, identification time: %r" %(numpy.average(sim), numpy.average(iden))