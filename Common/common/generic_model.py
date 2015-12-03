import sumpf
import common

class GenericModelClipping(object):
    def __init__(self, signal=None, thresholds=None, filters=None, amplificationfactor=None):

        if amplificationfactor is None:
            self.__amplificationfactor = 1.0
        else:
            self.__amplificationfactor = amplificationfactor
        self.__threshold = thresholds
        self.__signal = signal
        self.__fiterspec = filters
        self.__models = ['linearmodel','hammerstein','wiener','feedback']
        amplifier = sumpf.modules.AmplifySignal(input=self.__signal, factor=1.0)
        self.__adder = sumpf.modules.AddSignals()
        adder1 = sumpf.modules.AddSignals()
        adder2 = sumpf.modules.AddSignals()
        for i,model in enumerate(self.__models):
            clipper = sumpf.modules.ClipSignal(thresholds=self.__threshold)
            transform = sumpf.modules.FourierTransform()
            transform2 = sumpf.modules.FourierTransform()
            itransform = sumpf.modules.InverseFourierTransform()
            itransform2 = sumpf.modules.InverseFourierTransform()
            filterspec = sumpf.modules.MultiplySpectrums(spectrum2=filters)
            filterspec2 = sumpf.modules.MultiplySpectrums(spectrum2=filters)
            if model == 'linearmodel':
                amplifier.SetAmplificationFactor(factor=self.__amplificationfactor)
                sumpf.connect(amplifier.GetOutput, transform.SetSignal)
                sumpf.connect(transform.GetSpectrum, filterspec.SetInput1)
                sumpf.connect(filterspec.GetOutput, itransform.SetSpectrum)
                sumpf.connect(itransform.GetSignal, adder1.SetInput1)
                common.plot.log()
                common.plot.plot(filterspec.GetOutput(),show=False)
            elif model == 'hammerstein':
                sumpf.connect(amplifier.GetOutput, clipper.SetInput)
                sumpf.connect(clipper.GetOutput, transform.SetSignal)
                sumpf.connect(transform.GetSpectrum, filterspec.SetInput1)
                sumpf.connect(filterspec.GetOutput, itransform.SetSpectrum)
                sumpf.connect(itransform.GetSignal, adder1.SetInput2)
                common.plot.plot(filterspec.GetOutput(),show=False)
            elif model == 'wiener':
                sumpf.connect(amplifier.GetOutput, transform.SetSignal)
                sumpf.connect(transform.GetSpectrum, filterspec.SetInput1)
                sumpf.connect(filterspec.GetOutput, itransform.SetSpectrum)
                sumpf.connect(itransform.GetSignal, clipper.SetInput)
                sumpf.connect(clipper.GetOutput, adder2.SetInput1)
                common.plot.plot(sumpf.modules.FourierTransform(clipper.GetOutput()).GetSpectrum(),show=False)
            elif model == 'feedback':
                sumpf.connect(amplifier.GetOutput, transform.SetSignal)
                sumpf.connect(transform.GetSpectrum, filterspec.SetInput1)
                sumpf.connect(filterspec.GetOutput, itransform.SetSpectrum)
                sumpf.connect(itransform.GetSignal, clipper.SetInput)
                sumpf.connect(clipper.GetOutput, transform2.SetSignal)
                sumpf.connect(transform2.GetSpectrum, filterspec2.SetInput1)
                sumpf.connect(filterspec2.GetOutput, itransform2.SetSpectrum)
                sumpf.connect(itransform2.GetSignal, adder2.SetInput2)
                common.plot.plot(filterspec2.GetOutput(),show=False)
        sumpf.connect(self.__adder.SetInput1, adder1.GetOutput)
        sumpf.connect(self.__adder.SetInput2, adder2.GetOutput)
        common.plot.plot(sumpf.modules.FourierTransform(self.__adder.GetOutput()).GetSpectrum(),show=False)
        self.GetOutput = self.__adder.GetOutput
class GenericModelPolynomials(object):
    def __init__(self, signal=None, powers=None, filters=None, amplificationfactor=None):

        if amplificationfactor is None:
            self.__amplificationfactor = 1.0
        else:
            self.__amplificationfactor = amplificationfactor
        self.__powers = powers
        self.__signal = signal
        self.__fiterspec = filters
        self.__models = ['linearmodel','hammerstein','wiener','feedback']
        amplifier = sumpf.modules.AmplifySignal(input=self.__signal, factor=1.0)
        self.__adder = sumpf.modules.AddSignals()
        adder1 = sumpf.modules.AddSignals()
        adder2 = sumpf.modules.AddSignals()
        for i,model in enumerate(self.__models):
            polynomials = common.PolynomialOfSignal(signal=self.__signal,power=self.__powers)
            transform = sumpf.modules.FourierTransform()
            transform2 = sumpf.modules.FourierTransform()
            itransform = sumpf.modules.InverseFourierTransform()
            itransform2 = sumpf.modules.InverseFourierTransform()
            filterspec = sumpf.modules.MultiplySpectrums(spectrum2=filters)
            filterspec2 = sumpf.modules.MultiplySpectrums(spectrum2=filters)
            if model == 'linearmodel':
                amplifier.SetAmplificationFactor(factor=self.__amplificationfactor)
                sumpf.connect(amplifier.GetOutput, transform.SetSignal)
                sumpf.connect(transform.GetSpectrum, filterspec.SetInput1)
                sumpf.connect(filterspec.GetOutput, itransform.SetSpectrum)
                sumpf.connect(itransform.GetSignal, adder1.SetInput1)
                common.plot.log()
                common.plot.plot(filterspec.GetOutput(),show=False)
            elif model == 'hammerstein':
                sumpf.connect(amplifier.GetOutput, polynomials.SetInput)
                sumpf.connect(polynomials.GetOutput, transform.SetSignal)
                sumpf.connect(transform.GetSpectrum, filterspec.SetInput1)
                sumpf.connect(filterspec.GetOutput, itransform.SetSpectrum)
                sumpf.connect(itransform.GetSignal, adder1.SetInput2)
                common.plot.plot(filterspec.GetOutput(),show=False)
            elif model == 'wiener':
                sumpf.connect(amplifier.GetOutput, transform.SetSignal)
                sumpf.connect(transform.GetSpectrum, filterspec.SetInput1)
                sumpf.connect(filterspec.GetOutput, itransform.SetSpectrum)
                sumpf.connect(itransform.GetSignal, polynomials.SetInput)
                sumpf.connect(polynomials.GetOutput, adder2.SetInput1)
                common.plot.plot(sumpf.modules.FourierTransform(polynomials.GetOutput()).GetSpectrum(),show=False)
            elif model == 'feedback':
                sumpf.connect(amplifier.GetOutput, transform.SetSignal)
                sumpf.connect(transform.GetSpectrum, filterspec.SetInput1)
                sumpf.connect(filterspec.GetOutput, itransform.SetSpectrum)
                sumpf.connect(itransform.GetSignal, polynomials.SetInput)
                sumpf.connect(polynomials.GetOutput, transform2.SetSignal)
                sumpf.connect(transform2.GetSpectrum, filterspec2.SetInput1)
                sumpf.connect(filterspec2.GetOutput, itransform2.SetSpectrum)
                sumpf.connect(itransform2.GetSignal, adder2.SetInput2)
                common.plot.plot(filterspec2.GetOutput(),show=False)
        sumpf.connect(self.__adder.SetInput1, adder1.GetOutput)
        sumpf.connect(self.__adder.SetInput2, adder2.GetOutput)
        common.plot.plot(sumpf.modules.FourierTransform(self.__adder.GetOutput()).GetSpectrum(),show=False)
        self.GetOutput = self.__adder.GetOutput