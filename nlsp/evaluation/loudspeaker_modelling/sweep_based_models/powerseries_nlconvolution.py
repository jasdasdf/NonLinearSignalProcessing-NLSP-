import sumpf
import nlsp
import common
import _common as nlspcommon



def loudspeakerevaluation():
    load = sumpf.modules.SignalFile(filename=common.get_filename("Visaton BF45", "Sweep20", 1),
                                    format=sumpf.modules.SignalFile.WAV_FLOAT)
    excitation = sumpf.modules.SplitSignal(data=load.GetSignal(), channels=[0]).GetOutput()
    response = sumpf.modules.SplitSignal(data=load.GetSignal(), channels=[1]).GetOutput()
    kernel = nlsp.nonlinearconvolution_powerseries_filter(excitation,response,[20.0,20000.0,branches])
    model_up = nlsp.HammersteinGroupModel_up(input_signal=excitation,
                                       nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                       filter_irs=kernel,max_harmonics=range(1,branches+1))
    model_lp = nlsp.HammersteinGroupModel_lp(input_signal=excitation,
                                       nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                       filter_irs=kernel,max_harmonics=range(1,branches+1),
                                       filterfunction=sumpf.modules.FilterGenerator.BUTTERWORTH(order=100),
                                       attenuation=0.0001)
    model = nlsp.HammersteinGroupModel(input_signal=excitation,
                                       nonlinear_functions=nlsp.nonlinearconvolution_powerseries_nlfunction(branches),
                                       filter_irs=kernel)
    print "Reference SNR %r" %nlsp.get_snr(excitation,response)
    print "Reference MSE %r" %nlsp.get_snr(excitation,response)
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,upsample: %r" \
          %(nlsp.get_snr(excitation,response),
            nlsp.get_snr(excitation,model_up.GetOutput()),
            nlsp.get_snr(response,model_up.GetOutput()))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,upsample: %r" \
          %(nlsp.mean_squared_error(excitation,response),
            nlsp.mean_squared_error(excitation,model_up.GetOutput()),
            nlsp.mean_squared_error(response,model_up.GetOutput()))
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,lp: %r" \
          %(nlsp.get_snr(excitation,response),
            nlsp.get_snr(excitation,model_lp.GetOutput()),
            nlsp.get_snr(response,model_lp.GetOutput()))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,lp: %r" \
          %(nlsp.mean_squared_error(excitation,response),
            nlsp.mean_squared_error(excitation,model_lp.GetOutput()),
            nlsp.mean_squared_error(response,model_lp.GetOutput()))
    print "SNR of nl model: %r and identified system: %r and btw nl and iden system,simple: %r" \
          %(nlsp.get_snr(excitation,response),
            nlsp.get_snr(excitation,model.GetOutput()),
            nlsp.get_snr(response,model.GetOutput()))
    print "MSE of nl model: %r and identified system: %r and btw nl and iden system,simple: %r" \
          %(nlsp.mean_squared_error(excitation,response),
            nlsp.mean_squared_error(excitation,model.GetOutput()),
            nlsp.mean_squared_error(response,model.GetOutput()))

branches = 5
loudspeakerevaluation()