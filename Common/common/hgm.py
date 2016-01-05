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
        self.__samplingrate = 48000
        self.__highestfreq = 24000
        self.__signallength = int(signal.GetDuration()*self.__samplingrate)
        print self.__signallength, self.__samplingrate
        for branch,spectrum in enumerate(filters):
            prp = sumpf.modules.ChannelDataProperties(signal_length=self.__signallength,samplingrate=self.__samplingrate)
            a = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BUTTERWORTH(order=20),frequency=(self.__highestfreq/(branch+1)),resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
#            a = sumpf.modules.FilterGenerator(sumpf.modules.FilterGenerator.BESSEL(order=20),frequency=(self.__highestfreq/(branch+1)),resolution=prp.GetResolution(),length=prp.GetSpectrumLength()).GetSpectrum()
            # common.plot.log()
            # common.plot.plot(a)
            af = sumpf.modules.MultiplySpectrums(spectrum2=a)
            at = sumpf.modules.FourierTransform(signal=self.__signal)
            ai = sumpf.modules.InverseFourierTransform()
            d = sumpf.modules.ResampleSignal(signal=self.__signal, samplingrate=(self.__samplingrate/(branch+1)))
            u = sumpf.modules.ResampleSignal(samplingrate=self.__samplingrate)
            p = common.PolynomialOfSignal(power=branch+1)
            t = sumpf.modules.FourierTransform()
            f = sumpf.modules.MultiplySpectrums(spectrum2=spectrum)
            i = sumpf.modules.InverseFourierTransform()
            sumpf.connect(at.GetSpectrum, af.SetInput1)
            sumpf.connect(af.GetOutput, ai.SetSpectrum)
#            sumpf.connect(ai.GetSignal, d.SetInput)
#            sumpf.connect(d.GetOutput, p.SetInput)
#            sumpf.connect(p.GetOutput, u.SetInput)
#            sumpf.connect(p.GetOutput, t.SetSignal)
#            sumpf.connect(t.GetSpectrum, f.SetInput1)
            sumpf.connect(ai.GetSignal,p.SetInput)
            sumpf.connect(p.GetOutput, t.SetSignal)
            sumpf.connect(t.GetSpectrum,f.SetInput1)
            sumpf.connect(f.GetOutput, i.SetSpectrum)
            # common.plot.log()
            # common.plot.plot(f.GetOutput())
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

class HammersteinGroupModel_Harmonics(object):
    def __init__(self, signal=None, branches=None, harmonics=None):
        self.__signal = signal
        if branches is None:
            self.__branches = len(harmonics)
        else:
            self.__branches = branches
        self.__harmonics = harmonics
        self.__powers = []
        self.__ffts = []
        self.__filterspec = []
        self.__iffts = []
        self.__sums = [None] * len(harmonics.GetChannels())

        for branch,spectrum in enumerate(harmonics.GetChannels()):
            spliter = sumpf.modules.SplitSpectrum(data=harmonics,channels=[branch])
            p = common.PolynomialOfSignal(power=branch+1,signal=self.__signal)
            t = sumpf.modules.FourierTransform()
            f = sumpf.modules.MultiplySpectrums(spectrum2=spliter.GetOutput())
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

#     def SetParameters(self, filters):
#         pairs = []
#         for i, f in enumerate(filters):
#             pairs.append((self.__filterspec[i].SetInput2, f))
#         sumpf.set_multiple_values(pairs)