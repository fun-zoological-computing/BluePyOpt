#!/usr/bin/env python
# coding: utf-8
import pandas as pd
pd.set_option('max_columns',None)
pd.set_option('max_rows',None)
import matplotlib.pyplot as plt
import seaborn as sns
cm = sns.light_palette("green", as_cmap=True)
import pickle
import glob
import os
import scipy

from neuronunit.optimization.optimization_management import instance_opt
from neuronunit.optimization.optimization_management import plot_as_normal
from neuronunit.optimization.optimization_management import inject_and_not_plot_model, which_key
from neuronunit.capabilities.spike_functions import get_spike_waveforms#
from neuronunit.optimization.optimization_management import TSD
from neuronunit.optimization.model_parameters import MODEL_PARAMS, BPO_PARAMS
from neuronunit.optimization.optimization_management import inject_and_not_plot_model, plot_as_normal
from neuronunit.optimization.optimization_management import inject_and_plot_model, plot_as_normal
from neuronunit.tests import *
import quantities as qt
from sciunit.scores import RelativeDifferenceScore, ZScore
from sciunit import TestSuite
from quantities import Hz,pA

cells = pickle.load(open("processed_multicellular_constraints.p","rb"))

#purk = TSD(cells['Cerebellum Purkinje cell'])#.tests
#purk_vr = purk["RestingPotentialTest"].observation['mean']

ncl5 = TSD(cells["Neocortex pyramidal cell layer 5-6"])
ncl5.name = str("Neocortex pyramidal cell layer 5-6")
ncl5_vr = ncl5["RestingPotentialTest"].observation['mean']

ca1 = TSD(cells["Hippocampus CA1 pyramidal cell"])
ca1.name = str("Hippocampus CA1 pyramidal cell")

ca1_vr = ca1["RestingPotentialTest"].observation['mean']
experimental_constraints= cells

'''

def make_observations_frame():
    list_of_dicts = []
    for k,v in cells.items():
        observations = {}
        for k1 in ca1.keys():
            vsd = TSD(v)
            if k1 in vsd.keys():
                vsd[k1].observation['mean']
                observations[k1] = vsd[k1].observation['mean']
                observations['name'] = k
        list_of_dicts.append(observations)
    df = pd.DataFrame(list_of_dicts)
    df = df.set_index('name').T
    s = df.style.background_gradient(cmap=cm)
    return s
'''
def make_allen():

  rt = RheobaseTest(observation={'mean':70*qt.pA,'std':70*qt.pA})
  tc = TimeConstantTest(observation={'mean':24.4*qt.ms,'std':24.4*qt.ms})
  ir = InputResistanceTest(observation={'mean':132*qt.MOhm,'std':132*qt.MOhm})
  rp = RestingPotentialTest(observation={'mean':-71.6*qt.mV,'std':77.5*qt.mV})

  allen_tests = [rt,tc,rp,ir]
  for t in allen_tests:
      t.score_type = RelativeDifferenceScore
  allen_suite482493761 = TestSuite(allen_tests)
  allen_suite482493761.name = "http://celltypes.brain-map.org/mouse/experiment/electrophysiology/482493761"
  rt = RheobaseTest(observation={'mean':190*qt.pA,'std':190*qt.pA})
  tc = TimeConstantTest(observation={'mean':13.8*qt.ms,'std':13.8*qt.ms})
  ir = InputResistanceTest(observation={'mean':132*qt.MOhm,'std':132*qt.MOhm})
  rp = RestingPotentialTest(observation={'mean':-77.5*qt.mV,'std':77.5*qt.mV})
  fi = FITest(observation={'mean':0.09*Hz/pA})#'std':77.5*qt.mV})

  allen_tests = [rt,tc,rp,ir]#,fi]
  for t in allen_tests:
      t.score_type = RelativeDifferenceScore
  #allen_tests[-1].score_type = ZScore
  allen_suite471819401 = TestSuite(allen_tests)
  allen_suite471819401.name = "http://celltypes.brain-map.org/mouse/experiment/electrophysiology/471819401"
  list_of_dicts = []
  cells={}
  cells['471819401'] = TSD(allen_suite471819401)
  cells['482493761'] = TSD(allen_suite482493761)

  allen_tests = [rt,fi]
  for t in allen_tests:
     t.score_type = RelativeDifferenceScore
  allen_suite3 = TestSuite(allen_tests)

  cells['3'] = TSD(allen_suite3)

  for k,v in cells.items():
      observations = {}
      for k1 in cells['482493761'].keys():
          vsd = TSD(v)
          if k1 in vsd.keys():
              vsd[k1].observation['mean']

              observations[k1] = np.round(vsd[k1].observation['mean'],2)
              observations['name'] = k
      list_of_dicts.append(observations)
  df = pd.DataFrame(list_of_dicts)
  df


  return allen_suite471819401,allen_suite482493761,df,cells

allen_suite471819401,allen_suite482493761,_,cells = make_allen()

NC=TSD(experimental_constraints["Neocortex pyramidal cell layer 5-6"])
NC.pop("InjectedCurrentAPWidthTest",None)
NC.pop("InjectedCurrentAPAmplitudeTest",None)
NC.pop("InjectedCurrentAPThresholdTest",None)
MU = 100
NGEN = 25




final_pop, hall_of_fame, logs, hist,best_ind,best_fit_val,opt = instance_opt(
    cells['471819401'],
    BPO_PARAMS,
    '471819401',
    "ADEXP",
    MU,
    NGEN,
    "IBEA",
    use_streamlit=False
    )
final_pop, hall_of_fame, logs, hist,best_ind,best_fit_val,opt = instance_opt(
    cells['3'],
    BPO_PARAMS,
    '3',
    "ADEXP",
    MU,
    NGEN,
    "IBEA",
    use_streamlit=False
    )

final_pop, hall_of_fame, logs, hist,best_ind,best_fit_val,opt = instance_opt(
    NC,
    BPO_PARAMS,
    "Neocortex pyramidal cell layer 5-6",
    "ADEXP",
    MU,
    NGEN,
    "IBEA",
    use_streamlit=False
    )



MU = 100
NGEN = 150
final_pop, hall_of_fame, logs, hist,best_ind,best_fit_val,opt = instance_opt(
    NC,
    BPO_PARAMS,
    "Neocortex pyramidal cell layer 5-6",
    "IZHI",
    MU,
    NGEN,
    "IBEA",
    use_streamlit=False
    )
final_pop, hall_of_fame, logs, hist,best_ind,best_fit_val,opt = instance_opt(
    NC,
    BPO_PARAMS,
    "Hippocampus CA1 pyramidal cell",
    "ADEXP",
    MU,
    NGEN,
    "IBEA",
    use_streamlit=False
    )
