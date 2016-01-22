import sumpf
import nlsp

class HammersteinGroupModel(object):
    """
    A class to generate the output of hammerstein group model with given nonlinear functions, filter impulse responses
    and maximum harmonics
    """

    def __init__(self, input_signal=None, nonlinear_functions=(nlsp.function_factory.power_series(1),),
                 filter_irs=None, max_harmonics=(1,)):
        """
        :param signal: the input signal
        :param nonlinear_functions: the tuple of nonlinear functions of hammerstein group models
        :param filter_irs: the tuple of filter impulse responses
        :param max_harmonics: the tuple of maximum harmonics
        :return:
        """
        if input_signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = input_signal
        self.inputstage = sumpf.modules.AmplifySignal(input=self.__signal)
        self.__nlfunctions = nonlinear_functions
        if filter_irs is None:
            self.__filter_irs = (sumpf.modules.ImpulseGenerator(length=len(input_signal)).GetSignal(),)
        else:
            self.__filter_irs = filter_irs
        self.__max_harmonics = max_harmonics

        if len(self.__nlfunctions) == len(self.__filter_irs) == len(self.__max_harmonics):
            self.__branches = len(self.__nlfunctions)
        else:
            print "the given arguments dont have same length"
        self.hmodels = []
        self.__sums = [None] * self.__branches

        for nl,ir,mh in zip(self.__nlfunctions,self.__filter_irs,self.__max_harmonics):
            h = nlsp.AliasCompensatingHammersteinModelUpandDown(input_signal=self.inputstage.GetOutput(),
                                                                nonlin_func=nl, max_harm=mh,
                                                                filter_impulseresponse=ir)
            self.hmodels.append(h)

        for i in reversed(range(len(self.hmodels)-1)):
            self.__a = sumpf.modules.AddSignals()
            # print "connecting hammerstein model %i to adder %i" % (i, i)
            sumpf.connect(self.hmodels[i].GetOutput, self.__a.SetInput1)
            if i == len(self.hmodels)-2:
                # print "connecting hammerstein model %i to adder %i" % (i+1, i)
                sumpf.connect(self.hmodels[i+1].GetOutput, self.__a.SetInput2)
            else:
                # print "connecting adder %i to adder %i" % (i+1, i)
                sumpf.connect(self.__sums[i+1].GetOutput, self.__a.SetInput2)
            self.__sums[i] = self.__a

        self.GetOutput = self.__sums[0].GetOutput

    @sumpf.Input(sumpf.Signal)
    def SetInput(self, signal):
        inputs = []
        for i in range(len(self.hmodels)):
            inputs.append((self.hmodels[i].SetInput, signal))
        sumpf.set_multiple_values(inputs)

    @sumpf.Input(tuple)
    def SetNLFunctions(self, nonlinearfunctions):
        nonlinfunc = []
        for i in range(len(self.hmodels)):
            nonlinfunc.append((self.hmodels[i].SetNLFunction, nonlinearfunctions[i]))
        sumpf.set_multiple_values(nonlinfunc)

    @sumpf.Input(tuple)
    def SetFilterIRS(self, impulseresponse):
        irs = []
        for i in range(len(self.hmodels)):
            irs.append((self.hmodels[i].SetFilterIR, impulseresponse[i]))
        sumpf.set_multiple_values(irs)

    @sumpf.Input(tuple)
    def SetMaximumHarmonics(self, maxharmonics):
        harmonics = []
        for i in range(len(self.hmodels)):
            harmonics.append((self.hmodels[i].SetMaximumHarmonic, maxharmonics[i]))
        sumpf.set_multiple_values(harmonics)

    @sumpf.Output(sumpf.Signal)
    def GetHammersteinBranchOutput(self, branchnumber):
        if branchnumber > self.__branches:
            print "The branch doesnot exists"
        else:
            return self.hmodels[branchnumber-1].GetOutput()