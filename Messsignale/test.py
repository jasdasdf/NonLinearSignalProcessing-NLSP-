import math
import numpy
import sumpf
import common

with numpy.load("seeds.npz") as s:
	print dict(s)
exit()

#  18.0 (44, 0.20086152264512408) (182, 0.16020633726140107) (14, 0.9801110361669705)
#  19.0 (241, 0.20052272569925186) (79, 0.15998829539127635) (156, 0.9944910893970604)
#  20.0 (134, 0.20030890280775135) (134, 0.15987106399603201) (200, 0.9960332072603029)
#  22.457637381 (151, 0.20005445676696335) (202, 0.15961517990138971) (239, 0.9958778376827027)

#seed = 1489	#3800
seed = 0
silence_length = sumpf.modules.DurationToLength(duration=0.03, samplingrate=48000).GetLength()
noisegenerator = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(mean=0.0, standard_deviation=0.2),
                                              samplingrate=48000)
rms = sumpf.modules.RootMeanSquare(integration_time=sumpf.modules.RootMeanSquare.FULL)
best_rms_seed = {}
best_arv_seed = {}
best_max_seed = {}
while True:
	do_print = False
	if seed % 10 == 0:
		print "Trying seed", seed
	for signal_length in [2 ** 18, 2 ** 19, 2 ** 20, 120 * 48000]:
		excitation_length = signal_length - silence_length
		noisegenerator.Seed(seed)
		noisegenerator.SetLength(excitation_length)
		noise = noisegenerator.GetSignal()
		minimum = min(noise.GetChannels()[0])
		maximum = max(noise.GetChannels()[0])
		if minimum > -1.0 and maximum < 1.0:
			rms.SetInput(noise)
			rms_value = rms.GetOutput().GetChannels()[0][0]
			arv_value = numpy.average(numpy.abs(noise.GetChannels()[0]))
			part = (maximum - minimum) / 2.0
			if signal_length in best_rms_seed:
				if best_rms_seed[signal_length][1] < rms_value:
					best_rms_seed[signal_length] = (seed, rms_value)
					do_print = True
			else:
				best_rms_seed[signal_length] = (seed, rms_value)
				do_print = True
			if signal_length in best_arv_seed:
				if best_arv_seed[signal_length][1] < arv_value:
					best_arv_seed[signal_length] = (seed, arv_value)
					do_print = True
			else:
				best_arv_seed[signal_length] = (seed, arv_value)
				do_print = True
			if signal_length in best_max_seed:
				if best_max_seed[signal_length][1] < part:
					best_max_seed[signal_length] = (seed, part)
					do_print = True
			else:
				best_max_seed[signal_length] = (seed, part)
				do_print = True
		else:
			break
	if do_print:
		print "New Seeds"
		for l in best_rms_seed:
			print " ", math.log(l, 2.0), best_rms_seed[l], best_arv_seed[l], best_max_seed[l]
		numpy.savez_compressed("seeds.npz",
		                       rms=best_rms_seed,
		                       arv=best_arv_seed,
		                       part=best_max_seed)
	seed += 1

