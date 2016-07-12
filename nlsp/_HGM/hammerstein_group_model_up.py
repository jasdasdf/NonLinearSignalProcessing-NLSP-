import sumpf
import nlsp

class HammersteinGroupModel_up(object):
    """
    Upsampling aliasing compensated Hammerstein group model.
    """

    def __init__(self, input_signal=None, nonlinear_functions=(nlsp.function_factory.power_series(1),),
                 filter_irs=None, max_harmonics=None, resampling_algorithm = sumpf.modules.ResampleSignal.SPECTRUM):
        """
        :param signal: the input signal
        :param nonlinear_functions: the tuple of nonlinear functions eg. (nlsp.function_factory.power_series(1),...)
        :param filter_irs: the tuple of filter impulse responses eg. (IR1,...)
        :param max_harmonics: the tuple of maximum harmonics eg. (1,...)
        :param resampling_algorithm: the algorithm which can be used to downsample and upsample the signal eg. sumpf.modules.ResampleSignal.SPECTRUM
        """
        if input_signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = input_signal
        self.inputstage = sumpf.modules.AmplifySignal(input=self.__signal)
        self.__nlfunctions = nonlinear_functions
        if filter_irs is None:
            self.__filter_irs = (sumpf.modules.ImpulseGenerator(length=len(self.__signal)).GetSignal(),)*len(self.__nlfunctions)
        else:
            self.__filter_irs = filter_irs
        self.__resampling_algorithm = resampling_algorithm
        if len(self.__nlfunctions) == len(self.__filter_irs):
            self.__branches = len(self.__nlfunctions)
        else:
            print "the given arguments dont have same length"
        if max_harmonics is None:
            self.__max_harmonics = range(1,self.__branches+1)
        else:
            self.__max_harmonics = max_harmonics
        self.hmodels = []
        self.__sums = [None] * self.__branches

        for nl,ir,mh in zip(self.__nlfunctions,self.__filter_irs,self.__max_harmonics):
            h = nlsp.AliasingCompensatedHM_upsampling(input_signal=self.inputstage.GetOutput(),
                                                                nonlin_func=nl, max_harm=mh,
                                                                filter_impulseresponse=ir,
                                                                resampling_algorithm=self.__resampling_algorithm)
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
        if len(self.hmodels) == 1:
            self.__sums[0] = self.hmodels[0]
        self.GetOutput = self.__sums[0].GetOutput

    @sumpf.Input(sumpf.Signal)
    def SetInput(self, signal):
        """
        Sets the input to the Hammerstein group model.
        :param signal: the input signal
        """
        inputs = []
        for i in range(len(self.hmodels)):
            inputs.append((self.hmodels[i].SetInput, signal))
        sumpf.set_multiple_values(inputs)

    @sumpf.Input(tuple)
    def SetNLFunctions(self, nonlinearfunctions):
        """
        Sets the nonlinear functions of the Hammerstein group model.
        :param nonlinearfunctions: the tuple of nonlinear functions eg. (nlsp.function_factory.power_series(1),...)
        """
        nonlinfunc = []
        for i in range(len(self.hmodels)):
            nonlinfunc.append((self.hmodels[i].SetNLFunction, nonlinearfunctions[i]))
        sumpf.set_multiple_values(nonlinfunc)

    @sumpf.Input(tuple)
    def SetFilterIRS(self, impulseresponse):
        """
        Sets the impulse response of the linear blocks of the Hammerstein group model.
        :param impulseresponse: the tuple of filter impulse responses eg. (IR1,...)
        :return:
        """
        irs = []
        for i in range(len(self.hmodels)):
            irs.append((self.hmodels[i].SetFilterIR, impulseresponse[i]))
        sumpf.set_multiple_values(irs)

    @sumpf.Input(tuple)
    def SetMaximumHarmonics(self, maxharmonics):
        """
        Sets the maximum orders of distortions produced by the nonlinear function.
        :param maxharmonics:  the tuple of maximum harmonics eg. (1,...)
        """
        harmonics = []
        for i in range(len(self.hmodels)):
            harmonics.append((self.hmodels[i].SetMaximumHarmonic, maxharmonics[i]))
        sumpf.set_multiple_values(harmonics)

    @sumpf.Input(int)
    def GetHammersteinBranchOutput(self, branch):
        """
        Get the output of the individual branches of the Hammerstein group model.
        :param branchnumber: the branch number
        :return: the output of the particular branch of the Hammerstein group model
        """
        if branch > self.__branches:
            print "The branch doesnot exists"
        else:
            return self.hmodels[branch-1].GetOutput()

    @sumpf.Input(int)
    def GetHammersteinBranchNLOutput(self, branchnumber):
        """
        Get the output of the nonlinear block of certain branch of the Hammerstein group model.
        :param branchnumber: the branch number
        :return: the output of the nonlinear block of certain branch of the Hammerstein group model
        """
        if branchnumber > self.__branches:
            print "The branch doesnot exists"
        else:
            return self.hmodels[branchnumber-1].GetNLOutput()