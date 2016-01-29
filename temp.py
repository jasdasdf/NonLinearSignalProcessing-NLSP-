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


