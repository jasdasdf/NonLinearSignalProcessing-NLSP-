import sumpf
import common

class HammersteinGroupModel(object):
    def __init__(self, signal=None, branches=None, filters=None):
        self.__signal = signal
        if branches is None:
            self.__branches = len(filters)
        else:
            self.__branches = branches
        self.__powers = []
        self.__ffts = []
        self.__filterspec = []
        self.__iffts = []
        self.__sums = [None] * len(filters)

        for branch,spectrum in enumerate(filters):
            p = common.PolynomialOfSignal(power=branch+1,signal=self.__signal)
            t = sumpf.modules.FourierTransform()
            f = sumpf.modules.MultiplySpectrums(spectrum2=spectrum)
            i = sumpf.modules.InverseFourierTransform()
            sumpf.connect(p.GetOutput, t.SetSignal)
            sumpf.connect(t.GetSpectrum, f.SetInput1)
            sumpf.connect(f.GetOutput, i.SetSpectrum)
            self.__powers.append(p)
            self.__ffts.append(t)
            self.__filterspec.append(f)
            self.__iffts.append(i)
        for i in reversed(range(len(self.__filterspec)-1)):
            a = sumpf.modules.AddSignals()
#            print "connecting ifft %i to adder %i" % (i, i)
            sumpf.connect(self.__iffts[i].GetSignal, a.SetInput1)
            if i == len(self.__filterspec)-2:
#                print "connecting ifft %i to adder %i" % (i+1, i)
                sumpf.connect(self.__iffts[i+1].GetSignal, a.SetInput2)
            else:
#                print "connecting adder %i to adder %i" % (i+1, i)
                sumpf.connect(self.__sums[i+1].GetOutput, a.SetInput2)
            self.__sums[i] = a

        # make the input and output methods of the signal processing chain available
        self.SetInput = p.SetInput
        self.GetOutput = self.__sums[0].GetOutput

    def SetParameters(self, filters):
        pairs = []
        for i, f in enumerate(filters):
            pairs.append((self.__filterspec[i].SetInput2, f))
        sumpf.set_multiple_values(pairs)