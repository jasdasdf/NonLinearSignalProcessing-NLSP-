import sumpf
import common
import math
import sympy
from sympy import Symbol
from sympy.solvers import solve
import nlsp

frequency = 1000
max_harm = 4
samplingrate = 48000.0
length = 24000
gen_sine = sumpf.modules.SineWaveGenerator(frequency=frequency,
                                      phase=0.0,
                                      samplingrate=samplingrate,
                                      length=length)
gen_sine_spec = sumpf.modules.FourierTransform(signal=gen_sine.GetSignal())
gen_cosine = sumpf.modules.SineWaveGenerator(frequency=frequency,
                                      phase=90.0,
                                      samplingrate=samplingrate,
                                      length=length)

# nonlin = nlsp.NonlinearFunction.nonlinearfunc(2,"power")
# nonlin.SetInput(gen_sine.GetSignal())
# common.plot.log()
# common.plot.plot(sumpf.modules.FourierTransform(signal=nonlin.GetOutput()).GetSpectrum())
# nonlin.SetMaximumHarmonic(5)
# nonlin.SetNonlinearFunction("hermite")


sweep = sumpf.modules.SweepGenerator(samplingrate=48000,length=48000)
up = sumpf.modules.ResampleSignal(signal=sweep.GetSignal(),samplingrate=96000).GetOutput()
common.plot.plot(sweep.GetSignal())
common.plot.plot(up)

#
# common.plot.log()
# common.plot.plot(sumpf.modules.FourierTransform(signal=nonlin.GetOutput()).GetSpectrum())

