import unittest
#!/usr/bin/env python
# coding: utf-8
import matplotlib
matplotlib.use('Agg')
from bluepyopt.allenapi.allen_data_driven import opt_setup, opt_setup_two, opt_exec, opt_to_model
from neuronunit.optimization.optimization_management import check_bin_vm15
from neuronunit.optimization.model_parameters import MODEL_PARAMS, BPO_PARAMS, to_bpo_param
from neuronunit.optimization.optimization_management import dtc_to_rheo,inject_and_plot_model
from bluepyopt.allenapi.allen_data_driven import opt_to_model
from bluepyopt.allenapi.utils import dask_map_function
import numpy as np
from neuronunit.optimization.data_transport_container import DataTC
import efel
from jithub.models import model_classes
import matplotlib.pyplot as plt
import quantities as qt

class testOptimizationBackend(unittest.TestCase):
    def setUp(self):
        self = self
        self.ids = [ 324257146,
                325479788,
                476053392,
                623893177,
                623960880,
                482493761,
                471819401
               ]

    def test_opt_1(self):
        specimen_id = self.ids[1]
        cellmodel = "ADEXP"

        if cellmodel == "IZHI":
            model = model_classes.IzhiModel()
        if cellmodel == "MAT":
            model = model_classes.MATModel()
        if cellmodel == "ADEXP":
            model = model_classes.ADEXPModel()

        specific_filter_list = ['ISI_log_slope_1.5x',
                                'mean_frequency_1.5x',
                                'adaptation_index2_1.5x',
                                'first_isi_1.5x',
                                'ISI_CV_1.5x',
                                'median_isi_1.5x',
                                'Spikecount_1.5x',
                                'all_ISI_values',
                                'ISI_values',
                                'time_to_first_spike',
                                'time_to_last_spike',
                                'time_to_second_spike',
                                'spike_times']
        simple_yes_list = specific_filter_list
        target_num_spikes = 8
        dtc = DataTC()
        dtc.backend = cellmodel
        dtc._backend = model._backend
        dtc.attrs = model.attrs
        dtc.params = {k:np.mean(v) for k,v in MODEL_PARAMS[cellmodel].items()}
        dtc = dtc_to_rheo(dtc)
        vm,plt,dtc = inject_and_plot_model(dtc,plotly=False)
        fixed_current = 122 *qt.pA
        model, suite, nu_tests, target_current, spk_count = opt_setup(specimen_id,
                                                                      cellmodel,
                                                                      target_num_spikes,provided_model=model,fixed_current=False)
        model = dtc.dtc_to_model()
        model.seeded_current = target_current['value']
        model.allen = True
        model.seeded_current
        model.NU = True
        cell_evaluator,simple_cell = opt_setup_two(model,cellmodel, suite, nu_tests, target_current, spk_count,provided_model=model)
        NGEN = 15
        MU = 12

        mapping_funct = dask_map_function
        final_pop, hall_of_fame, logs, hist = opt_exec(MU,NGEN,mapping_funct,cell_evaluator)
        opt,target = opt_to_model(hall_of_fame,cell_evaluator,suite, target_current, spk_count)
        best_ind = hall_of_fame[0]
        fitnesses = cell_evaluator.evaluate_with_lists(best_ind)
        assert np.sum(fitnesses)<0.7
        self.assertGreater(0.7,np.sum(fitnesses))

        #obnames = [obj.name for obj in cell_evaluator.objectives]

        gen_numbers = logs.select('gen')
        min_fitness = logs.select('min')
        max_fitness = logs.select('max')
        avg_fitness = logs.select('avg')
        plt.plot(gen_numbers, max_fitness, label='max fitness')
        plt.plot(gen_numbers, avg_fitness, label='avg fitness')
        plt.plot(gen_numbers, min_fitness, label='min fitness')
        plt.plot(gen_numbers, min_fitness, label='min fitness')
        plt.semilogy()
        plt.xlabel('generation #')
        plt.ylabel('score (# std)')
        plt.legend()
        plt.xlim(min(gen_numbers) - 1, max(gen_numbers) + 1)
        #model = opt.dtc_to_model()
        plt.plot(opt.vm15.times,opt.vm15)
        plt.plot(opt.vm15.times,opt.vm15)
        target.vm15 = suite.traces['vm15']
        plt.plot(target.vm15.times,target.vm15)
        target.vm15 = suite.traces['vm15']
        check_bin_vm15(target,opt)
if __name__ == '__main__':
    unittest.main()
