import numpy
import itertools
import sumpf
import nlsp

# Applicable to only virtual nonlinear system
# Find Uniqueness between reference and identified nonlinear system

def filterkernel_evaluation_plot(reference_kernels, identified_kernels, Plot="total"):
    """
    plot the difference between te reference and identified filter kernels
    :param reference_kernels: the array of reference filter kernels
    :param identified_kernels: the array of identified filter kernels
    :param Plot: either "individual" or "total"
    :return:
    """
    dummy_sum = sumpf.modules.ConstantSignalGenerator(value=0.0, samplingrate=reference_kernels[0].GetSamplingRate(),
                                                      length=len(reference_kernels[0])).GetSignal()
    identified_kernels = nlsp.change_length_filterkernels(identified_kernels,len(reference_kernels[0]))
    for i,(reference_kernel, identified_kernel) in enumerate(zip(reference_kernels,identified_kernels)):
        sub = identified_kernel - reference_kernel
        dummy_sum = sub + dummy_sum
        # sub = sumpf.modules.FourierTransform(sub).GetSpectrum()
        # print nlsp.calculateenergy_freq(sub),i
        if Plot is "individual":
            nlsp.common.plots.relabelandplot(reference_kernel,"kernel %d reference"%(i+1),show=False)
            nlsp.common.plots.relabelandplot(identified_kernel,"kernel %d identified"%(i+1),show=False)
            nlsp.common.plots.relabelandplot(sub,"kernel %d difference" %(i+1),show=True)
        elif Plot is "total":
            nlsp.common.plots.relabelandplot(sub,"kernel %d difference" %(i+1),show=False)
    if Plot is "total":
        nlsp.common.plots.relabelandplot(dummy_sum,"diff_sum",show=True,line='g^')

def filterkernel_evaluation_sum(reference_kernels, identified_kernels, Plot=False):
    """
    calculate the SNR of parallel filter kernels
    :param reference_kernels: the array of reference filter kernel
    :param identified_kernels: the array of identified filter kernel
    :param Plot: either True or False
    :return:
    """
    identified_kernels = nlsp.change_length_filterkernels(identified_kernels,len(reference_kernels[0]))
    temp_identified = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=identified_kernels[0].GetSamplingRate(),
                                                            length=len(identified_kernels[0])).GetSignal()
    temp_reference = sumpf.modules.ConstantSignalGenerator(value=0.0,samplingrate=reference_kernels[0].GetSamplingRate(),
                                                            length=len(reference_kernels[0])).GetSignal()
    snr_diff = []
    for i,(reference_kernel, identified_kernel) in enumerate(zip(reference_kernels,identified_kernels)):
        snr_diff.append(nlsp.snr(reference_kernel,identified_kernel)[0])
        temp_reference = temp_reference + reference_kernel
        temp_identified = temp_identified + identified_kernel
    temp_identified = sumpf.modules.FourierTransform(temp_identified).GetSpectrum()
    temp_reference = sumpf.modules.FourierTransform(temp_reference).GetSpectrum()
    if Plot is True:
        nlsp.common.plots.relabelandplot(temp_identified,"identified sum",show=False)
        nlsp.common.plots.relabelandplot(temp_reference,"reference sum",show=True)
    print "SNR between summed reference and identified kernels %r" %nlsp.snr(temp_reference,temp_identified)
    print "Mean SNR between reference and identified kernels %r,Individual SNR: %r" %(numpy.mean(snr_diff),snr_diff)
