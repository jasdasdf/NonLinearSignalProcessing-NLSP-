import sumpf

class HammersteinGroup_Series(object):

    def __init__(self, input_signal=None,
                 nonlinear_functions=None,
                 filter_irs=None,
                 max_harmonics=None,
                 hgm_type=None):
        if input_signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = input_signal
        self.inputstage = sumpf.modules.AmplifySignal(input=self.__signal)
        self.__nlfunctions = nonlinear_functions
        self.__maxharmonics = max_harmonics
        if filter_irs is None:
            self.__filter_irs = ((sumpf.modules.ImpulseGenerator(length=len(input_signal)).GetSignal(),),
                                 (sumpf.modules.ImpulseGenerator(length=len(input_signal)).GetSignal(),))
        else:
            self.__filter_irs = filter_irs
        if len(self.__nlfunctions) == len(self.__filter_irs):
            self.__segments = len(self.__nlfunctions)
        else:
            print "the given arguments dont have same length"
        self.__hgm = hgm_type
        self.hmodels = []

        for i,(nl,ir,mh) in enumerate(zip(self.__nlfunctions,self.__filter_irs,self.__maxharmonics)):
            h = self.__hgm[i](nonlinear_functions=nl, filter_irs=ir, max_harmonics=mh)
            h.SetInput(self.inputstage.GetOutput())
            self.hmodels.append(h)
            self.inputstage.SetInput(h.GetOutput())

    def GetOutput(self,segment):
        return self.hmodels[segment-1].GetOutput()