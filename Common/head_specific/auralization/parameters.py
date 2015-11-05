import math
import sumpf
from determination import flags, ParameterSet, KnownValue, UnknownLimitedValue, AirDensity, \
                          UnknownVoiceCoilInductanceGenerator, UnknownForceFactorGenerator, \
                          UnknownSuspensionStiffnessGenerator, UnknownMechanicalDampingGenerator, \
                          KnownVoiceCoilInductanceGenerator, KnownForceFactorGenerator, \
                          KnownSuspensionStiffnessGenerator, KnownMechanicalDampingGenerator
import head_specific

def get_parameters(speaker_name):
	resonance_frequency = head_specific.get_resonance_frequency(speaker_name)
	if speaker_name == "Commander Keen":
		maximum_linear_excursion = 0.0007
		air_gap_height = 0.002
		parameters = ParameterSet(voicecoil_resistance=KnownValue(value=4.0, dictionary_key="R"),
		                          voicecoil_inductance=KnownVoiceCoilInductanceGenerator(L0=6.442925768092364e-05, L1=-6.7320477809347223e-11, L2=-1.5715665099657321e-07, L3=3.0823716024341544e-06, L4=-0.064444635413359166, Lv=-5.0762940618337214e-14, LV=-7.125047527890651e-14),
		                          force_factor=KnownForceFactorGenerator(M0=0.8975628614309394, M1=59.537475518052986, M2=-184135.75384139159, M3=56092354.325108454, M4=-515891402729.79102),
		                          suspension_stiffness=KnownSuspensionStiffnessGenerator(k0=2208.43078384199, k1=-1289288.1855131099, k2=792413974.29286146),
		                          mechanical_damping=KnownMechanicalDampingGenerator(w0=0.10094305348301001, w2=0.016113859195488658),
		                          diaphragm_mass=KnownValue(value=0.0004161230312110606, dictionary_key="m"),
		                          diaphragm_area=KnownValue(value=math.pi * 0.02 ** 2, dictionary_key="S"),
		                          listener_distance=KnownValue(value=0.067, dictionary_key="r"),
		                          medium_density=AirDensity(temperature=23.0, relative_humidity=0.7, atmospheric_pressure=99300.0))
#		parameters = ParameterSet(#voicecoil_resistance=UnknownLimitedValue(value=4.0, limits=(3.8, 4.05), dictionary_key="R"),
#		                          voicecoil_resistance=KnownValue(value=4.0, dictionary_key="R"),
#		                          voicecoil_inductance=UnknownVoiceCoilInductanceGenerator.Factory(voicecoil_inductance=60.0e-6, voicecoil_inductance_limits=(1.0e-6, 500.0e-6), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
#		                          force_factor=UnknownForceFactorGenerator.Factory(force_factor=1.3, force_factor_limits=(0.3, 12.0), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
#		                          suspension_stiffness=UnknownSuspensionStiffnessGenerator.Factory(suspension_stiffness=4300.0, suspension_stiffness_limits=(500.0, 7000.0), maximum_linear_excursion=maximum_linear_excursion),
#		                          mechanical_damping=UnknownMechanicalDampingGenerator.Factory(mechanical_damping=0.19, mechanical_damping_limits=(0.015, 3.5), maximum_linear_excursion=maximum_linear_excursion, resonance_frequency=resonance_frequency),
#		                          diaphragm_mass=UnknownLimitedValue(value=0.0008, limits=(0.00005, 0.005), dictionary_key="m"),
##		                          diaphragm_area=UnknownLimitedValue(value=math.pi * 0.02 ** 2, limits=(math.pi * 0.018 ** 2, math.pi * 0.0225 ** 2), dictionary_key="S"),
#		                          listener_distance=KnownValue(value=0.067, dictionary_key="r"),
#		                          medium_density=AirDensity(temperature=23.0, relative_humidity=0.7, atmospheric_pressure=99300.0))
		return parameters
	elif speaker_name == "Visaton BF45":
		maximum_linear_excursion = 0.001
		air_gap_height = 0.002
		parameters = ParameterSet(#voicecoil_resistance=UnknownLimitedValue(value=3.4, limits=(3.2, 3.6), dictionary_key="R"),
		                          voicecoil_resistance=KnownValue(value=3.4, dictionary_key="R"),
#		                          voicecoil_inductance=UnknownLimitedValue(value=40.0e-6, limits=(1.0e-6, 500.0e-6), dictionary_key="L0"),
		                          voicecoil_inductance=UnknownVoiceCoilInductanceGenerator.Factory(voicecoil_inductance=40.0e-6, voicecoil_inductance_limits=(1.0e-6, 500.0e-6), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
#		                          force_factor=UnknownLimitedValue(value=2.4, limits=(0.3, 10.0), dictionary_key="M0"),
		                          force_factor=UnknownForceFactorGenerator.Factory(force_factor=2.4, force_factor_limits=(0.3, 10.0), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
#		                          suspension_stiffness=UnknownLimitedValue(value=3800.0, limits=(500.0, 7000.0), dictionary_key="k0"),
		                          suspension_stiffness=UnknownSuspensionStiffnessGenerator.Factory(suspension_stiffness=3800.0, suspension_stiffness_limits=(500.0, 7000.0), maximum_linear_excursion=maximum_linear_excursion),
#		                          mechanical_damping=UnknownLimitedValue(value=1.1, limits=(0.015, 3.5), dictionary_key="k0"),
		                          mechanical_damping=UnknownMechanicalDampingGenerator.Factory(mechanical_damping=1.1, mechanical_damping_limits=(0.015, 3.5), maximum_linear_excursion=maximum_linear_excursion, resonance_frequency=resonance_frequency),
		                          diaphragm_mass=UnknownLimitedValue(value=0.0025, limits=(0.0001, 0.005), dictionary_key="m"),
		                          diaphragm_area=KnownValue(value=math.pi * 0.02 ** 2, dictionary_key="S"),
#		                          diaphragm_area=UnknownLimitedValue(value=math.pi * 0.02 ** 2, limits=(math.pi * 0.018 ** 2, math.pi * 0.0225 ** 2), dictionary_key="S"),
		                          listener_distance=KnownValue(value=0.07, dictionary_key="r"),
		                          medium_density=AirDensity(temperature=23.0, relative_humidity=0.7, atmospheric_pressure=99300.0))
		return parameters
	elif speaker_name == "Sonavox Low":
		maximum_linear_excursion = 0.0035
		air_gap_height = 0.008
		parameters = ParameterSet(#voicecoil_resistance=UnknownLimitedValue(value=2.95, limits=(2.7, 3.1), dictionary_key="R"),
		                          voicecoil_resistance=KnownValue(value=2.95, dictionary_key="R"),
#		                          voicecoil_inductance=UnknownLimitedValue(value=0.625e-3, limits=(10.0e-6, 5.0e-3), dictionary_key="L"),
		                          voicecoil_inductance=UnknownVoiceCoilInductanceGenerator.Factory(voicecoil_inductance=0.625e-3, voicecoil_inductance_limits=(10.0e-6, 5.0e-3), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
#		                          force_factor=UnknownLimitedValue(value=7.767, limits=(1.0, 25.0), dictionary_key="M"),
		                          force_factor=UnknownForceFactorGenerator.Factory(force_factor=7.767, force_factor_limits=(1.0, 25.0), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
#		                          suspension_stiffness=UnknownLimitedValue(value=1540.0, limits=(300.0, 5000.0), dictionary_key="k"),
		                          suspension_stiffness=UnknownSuspensionStiffnessGenerator.Factory(suspension_stiffness=1540.0, suspension_stiffness_limits=(300.0, 5000.0), maximum_linear_excursion=maximum_linear_excursion),
#		                          mechanical_damping=UnknownLimitedValue(value=0.64, limits=(0.15, 4.0), dictionary_key="w"),
		                          mechanical_damping=UnknownMechanicalDampingGenerator.Factory(mechanical_damping=0.64, mechanical_damping_limits=(0.15, 4.0), maximum_linear_excursion=maximum_linear_excursion, resonance_frequency=resonance_frequency),
		                          diaphragm_mass=UnknownLimitedValue(value=0.02, limits=(0.001, 0.05), dictionary_key="m"),
		                          diaphragm_area=KnownValue(value=math.pi * 0.0775 ** 2, dictionary_key="S"),
#		                          diaphragm_area=UnknownLimitedValue(value=math.pi * 0.08 ** 2, limits=(math.pi * 0.066 ** 2, math.pi * 0.083 ** 2), dictionary_key="S"),
		                          listener_distance=KnownValue(value=0.4, dictionary_key="r"),
		                          medium_density=AirDensity(temperature=23.0, relative_humidity=0.7, atmospheric_pressure=99300.0))
		return parameters
	elif speaker_name == "Sonavox Mid":
		maximum_linear_excursion = 0.003
		air_gap_height = 0.008
		parameters = ParameterSet(#voicecoil_resistance=UnknownLimitedValue(value=3.0, limits=(2.8, 3.2), dictionary_key="R"),
		                          voicecoil_resistance=KnownValue(value=3.0, dictionary_key="R"),
		                          voicecoil_inductance=UnknownVoiceCoilInductanceGenerator.Factory(voicecoil_inductance=0.1e-3, voicecoil_inductance_limits=(10.0e-6, 5.0e-3), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
		                          force_factor=UnknownForceFactorGenerator.Factory(force_factor=4.0, force_factor_limits=(1.0, 20.0), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
		                          suspension_stiffness=UnknownSuspensionStiffnessGenerator.Factory(suspension_stiffness=1500.0, suspension_stiffness_limits=(300.0, 5000.0), maximum_linear_excursion=maximum_linear_excursion),
		                          mechanical_damping=UnknownMechanicalDampingGenerator.Factory(mechanical_damping=0.7, mechanical_damping_limits=(0.15, 4.0), maximum_linear_excursion=maximum_linear_excursion, resonance_frequency=resonance_frequency),
		                          diaphragm_mass=UnknownLimitedValue(value=0.018, limits=(0.001, 0.1), dictionary_key="m"),
		                          diaphragm_area=KnownValue(value=math.pi * 0.0775 ** 2, dictionary_key="S"),
#		                          diaphragm_area=UnknownLimitedValue(value=math.pi * 0.08 ** 2, limits=(math.pi * 0.066 ** 2, math.pi * 0.083 ** 2), dictionary_key="S"),
		                          listener_distance=KnownValue(value=0.4, dictionary_key="r"),
		                          medium_density=AirDensity(temperature=23.0, relative_humidity=0.7, atmospheric_pressure=99300.0))
		return parameters
	elif speaker_name == "Sonavox High":
		maximum_linear_excursion = 0.0005
		air_gap_height = 0.001
		parameters = ParameterSet(#voicecoil_resistance=UnknownLimitedValue(value=3.2, limits=(3.0, 3.4), dictionary_key="R"),
		                          voicecoil_resistance=KnownValue(value=3.2, dictionary_key="R"),
		                          voicecoil_inductance=UnknownVoiceCoilInductanceGenerator.Factory(voicecoil_inductance=10.0e-6, voicecoil_inductance_limits=(1.0e-6, 500.0e-6), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
		                          force_factor=UnknownForceFactorGenerator.Factory(force_factor=0.6, force_factor_limits=(0.3, 10.0), maximum_linear_excursion=maximum_linear_excursion, air_gap_height=air_gap_height),
		                          suspension_stiffness=UnknownSuspensionStiffnessGenerator.Factory(suspension_stiffness=6800.0, suspension_stiffness_limits=(1000.0, 10.0e3), maximum_linear_excursion=maximum_linear_excursion),
		                          mechanical_damping=UnknownMechanicalDampingGenerator.Factory(mechanical_damping=0.5, mechanical_damping_limits=(0.015, 3.5), maximum_linear_excursion=maximum_linear_excursion, resonance_frequency=resonance_frequency),
		                          diaphragm_mass=UnknownLimitedValue(value=0.083e-3, limits=(0.05e-3, 0.001), dictionary_key="m"),
		                          diaphragm_area=KnownValue(value=math.pi * 0.01 ** 2, dictionary_key="S"),
#		                          diaphragm_area=UnknownLimitedValue(value=math.pi * 0.01 ** 2, limits=(math.pi * 0.007 ** 2, math.pi * 0.012 ** 2), dictionary_key="S"),
		                          listener_distance=KnownValue(value=0.056, dictionary_key="r"),
		                          medium_density=AirDensity(temperature=23.0, relative_humidity=0.7, atmospheric_pressure=99300.0))
		return parameters
	else:
		raise ValueError("Unknown speaker: %s" % str(speaker_name))

def get_determined_parameters(speaker_name):
	raise RuntimeError("This function is no longer needed")

