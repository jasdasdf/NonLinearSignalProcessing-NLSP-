import sumpf

class HammersteinGroup_Series(object):
    """
    Class to connect Hammerstein Group Models in series
    """
    def __init__(self, input_signal=None,
                 nonlinear_functions=None,
                 filter_irs=None,
                 max_harmonics=None,
                 hgm_type=None):
        """
        :param input_signal: the input signal
        :param nonlinear_functions: the tuple of nonlinear functions to hgm
        :param filter_irs: the tuple of filter impulse response to hgm
        :param max_harmonics: the tuple of max harmonics to hgm
        :param hgm_type: the type of hammerstein group model, eg. nlsp.HammersteinGroupModel_up
        """
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
        """
        Get output method of the hammerstein group model connected in series
        :param segment: the segment of hgm
        :return: the output of corresponding hgm
        """
        return self.hmodels[segment-1].GetOutput()