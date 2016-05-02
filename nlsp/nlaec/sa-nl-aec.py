import nlsp
import sumpf
import nlsp.common.plots as plot

def combination(hgm, filter_kernels, branches):

    nl_outputs = []
    for i in range(branches):
        nl_outputs.append(hgm.GetHammersteinBranchNLOutput(i+1))
    W = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=nl_outputs[0].GetSamplingRate(),
                                                         length=len(nl_outputs[0])).GetSignal()
    for i,filt in enumerate(filter_kernels):
        num_dot = nlsp.dot_product(signal1=filt,signal2=filter_kernels[0])
        den_dot = nlsp.dot_product(signal1=filter_kernels[0],signal2=filter_kernels[0])
        w = num_dot[0]/den_dot[0]
        constant = sumpf.modules.ConstantSignalGenerator(value=w,samplingrate=nl_outputs[i].GetSamplingRate(),
                                                         length=len(nl_outputs[i])).GetSignal()
        w = constant * nl_outputs[i]
        W = W + w
    return W


class SA_HammersteinGroupModel(object):

    def __init__(self, input_signal=None, output_signal=None, nonlinear_function=nlsp.function_factory.power_series,
                 adaptation_alg=nlsp.multichannel_nlms, branches=5, filtertaps=1024):

        self.__input_stage = sumpf.modules.AmplifySignal(factor=1.0)
        self.__output_stage = sumpf.modules.AmplifySignal(factor=1.0)
        if input_signal is None:
            self.__input_stage.SetInput(sumpf.Signal())
        else:
            self.__input_stage.SetInput(input_signal)
        if output_signal is None:
            self.__output_stage.SetInput(sumpf.Signal())
        else:
            self.__output_stage.SetInput(output_signal)
        self.__filtertaps = filtertaps
        self.__nl_function = nonlinear_function
        self.__adf_algorithm = adaptation_alg
        self.__branches = branches
        self.connect()

    def connect(self):
        impulse = sumpf.modules.ImpulseGenerator(samplingrate=self.__input_stage.GetOutput().GetSamplingRate(),length=self.__filtertaps).GetSignal()
        self.__hgm = nlsp.HammersteinGroupModel_up(nonlinear_functions=nlsp.nl_branches(self.__nl_function,branches),
                                                   filter_irs=[impulse,]*self.__branches)
        self.__hm = nlsp.HammersteinGroupModel_up(nonlinear_functions=[nlsp.function_factory.power_series(1),]*2,
                                                  filter_irs=[impulse,]*2)
        try:
            self.__kernel1
        except:
            print "not local kernel 1"
            self.__kernel1 = [sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=self.__input_stage.GetOutput().GetSamplingRate(),
                                                                    length=self.__filtertaps).GetSignal(),]*self.__branches
        self.__kernel1,nl = nlsp.adaptive_identification_powerseries(self.__input_stage.GetOutput(),self.__output_stage.GetOutput(),branches=self.__branches,
                                                 nonlinear_func=self.__nl_function, iterations=1, init_coeffs=self.__kernel1)
        self.__hgm.SetInput(self.__input_stage.GetOutput())
        self.__hgm.SetFilterIRS(self.__kernel1)
        input_hm = combination(self.__hgm,self.__kernel1,self.__branches)
        try:
            self.__kernel2
        except:
            print "not local kernel 2"
            self.__kernel2 = [sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=self.__input_stage.GetOutput().GetSamplingRate(),
                                                             length=self.__filtertaps).GetSignal(),]*2
        self.__kernel2,nl = nlsp.adaptive_identification_powerseries(input_hm,self.__output_stage.GetOutput(),branches=2,
                                                         nonlinear_func=self.__nl_function, iterations=1, init_coeffs=self.__kernel2)
        self.__hm.SetInput(input_hm)
        self.__hm.SetFilterIRS(self.__kernel2)
        self.__sa = sumpf.modules.AddSignals(self.__hm.GetHammersteinBranchOutput(1),self.__hgm.GetOutput())

    @sumpf.Input(sumpf.Signal())
    def SetInputOutput(self,input,output):
        self.__input_stage.SetInput(input)
        self.__output_stage.SetInput(output)
        self.connect()

    def GethmOutput(self):
        return self.__hm.GetOutput()

    def GetsaOutput(self):
        return self.__sa.GetOutput()



branches = 5
iteration = 2
input_generator = nlsp.NovakSweepGenerator_Sine(sampling_rate=48000.0, length=2**18, start_frequency=20.0,
                                   stop_frequency=20000.0, fade_out= 0.0,fade_in=0.0)
input_signal = input_generator.GetOutput()
filter_spec_tofind = nlsp.log_bpfilter(branches=5,input=input_signal)
ref_nlsystem = nlsp.HammersteinGroupModel_up(input_signal=input_signal,
                                             nonlinear_functions=nlsp.nl_branches(nlsp.function_factory.power_series,branches),
                                             filter_irs=filter_spec_tofind,
                                             max_harmonics=range(1,branches+1))
ec = SA_HammersteinGroupModel(input_signal=input_generator.GetOutput(),output_signal=ref_nlsystem.GetOutput(),nonlinear_function=nlsp.function_factory.power_series)
for i in range(iteration):
    ec.SetInputOutput(input_generator.GetOutput(),ref_nlsystem.GetOutput())
plot.relabelandplot(ref_nlsystem.GetOutput(),"ref",show=False)
plot.relabelandplot(ec.GethmOutput(),"hm_out",show=False)
plot.relabelandplot(ec.GetsaOutput(),"sa_out",show=True)
