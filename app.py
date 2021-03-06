"""
BPO front end for reduced neural models
"""  	

import pandas as pd
import numpy as np                       
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go # or plotly.express as px
import sklearn   
import os
# sense if running on heroku
if 'DYNO' in os.environ:
    heroku = False
else:
    heroku = True
import pickle
experimental_constraints = pickle.load(open("examples/data_driven/processed_multicellular_constraints.p","rb"))
import utils
import streamlit as st
import bluepyopt as bpop
from neuronunit.optimisation.model_parameters import MODEL_PARAMS
from neuronunit.optimisation.optimization_management import inject_and_plot_model, inject_and_plot_passive_model


import pandas as pd

from neuronunit.optimisation.optimization_management import TSD

def instance_opt(experimental_constraints,MODEL_PARAMS,test_key,model_value,MU,NGEN):
  cell_evaluator, simple_cell, score_calc, test_names = utils.make_evaluator(
                                                        experimental_constraints,
                                                        MODEL_PARAMS,
                                                        test_key,
                                                        model=model_value)
  #cell_evaluator, simple_cell, score_calc = make_evaluator(cells,MODEL_PARAMS)

  #MU =10
  mut = 0.05
  cxp = 0.1
  optimisation = bpop.optimisations.DEAPOptimisation(
          evaluator=cell_evaluator,
          offspring_size = MU,
          map_function = utils.dask_map_function,
          selector_name=diversity,
          mutpb=mut,
          cxpb=cxp)

  final_pop, hall_of_fame, logs, hist = optimisation.run(max_ngen=NGEN)
  best_ind = hall_of_fame[0]

  

  st.success("Model best fit to experiment {0}".format(test_key))
  st.markdown('\n\n\n\n')

  best_ind_dict = cell_evaluator.param_dict(best_ind)
  model = cell_evaluator.cell_model
  cell_evaluator.param_dict(best_ind)
  model.attrs = {str(k):float(v) for k,v in cell_evaluator.param_dict(best_ind).items()}
  opt = model.model_to_dtc()
  opt.attrs = {str(k):float(v) for k,v in cell_evaluator.param_dict(best_ind).items()}
  opt.tests = experimental_constraints
  obs_preds = opt.make_pretty(experimental_constraints)

  frame = opt.SA.to_frame()
  st.write(frame.T)

  obs_preds = opt.obs_preds
  st.write(obs_preds.T)

  vm,fig = inject_and_plot_model(opt,plotly=True)
  st.write(fig)

  #inject_and_plot_passive_model(opt,plotly=Tru)
  fig = inject_and_plot_passive_model(opt,opt,plotly=True)
  st.write(fig)

  #plt.show()
  st.markdown("""
  The optimal model parameterization is {0}    
  """.format(opt.attrs))

  st.markdown("""
  Model Performance Relative to fitting data {0}    
  """.format(sum(best_ind.fitness.values)/10*len(experimental_constraints)))
  # radio_value = st.sidebar.radtio("Target Number of Samples",[10,20,30])
  st.markdown("""
  This score is {0} worst score is {1}  
  """.format(sum(best_ind.fitness.values),10*len(experimental_constraints)))

if __name__ == "__main__":  
    st.title('Reduced Model Fitting to Data')
    experimental_constraints.pop("Olfactory bulb (main) mitral cell")
    #API_TOKEN = st.text_input('Please Enter Your Fitbit API token:')
    test_key = st.sidebar.radio("\
      What experiments would you like to fit models to?"
		,tuple(experimental_constraints.keys()))



    experimental_constraints = TSD(experimental_constraints[test_key])
    
    test_keys = list(experimental_constraints.keys())
    subset_tests = st.sidebar.radio("\
		Would you like to fit models on a subset of tests?"
		,("No","Yes"))
    if subset_tests == "Yes":
      test_keys = st.sidebar.multiselect("\
      Are you interested in less than all of the features?"
      ,tuple(experimental_constraints.keys()))


    experimental_constraints = [ experimental_constraints[k] for k in test_keys ]
    #st.text(test_keys)
    model_value = st.sidebar.radio("\
		Which models would you like to optimize"
		,("ADEXP","IZHI","NEURONHH"))

    diversity = st.sidebar.radio("\
		Do you want diverse solutions or just the best solution?"
		,("NSGA2","IBEA"))

    readiness = st.radio("\
		Ready to go?"
		,("No","Yes"))

    MU = st.sidebar.radio("\
		Population size is"
		,(10,50,100))
    NGEN = st.sidebar.radio("\
		Number of generations is"
		,(10,50,100))

    if readiness == "Yes":
      instance_opt(experimental_constraints,MODEL_PARAMS,test_key,model_value,MU,NGEN)
      
     
      if model_value == "ADEXP":
        st.markdown('''
        In the {2} Model:
        Over three different current injection strengths mean Model speed was {0}
        ms, to find unkown rheoase value it takes {1} seconds'''.format(300,3.8,model_value))


      if model_value == "IZHI":
        st.markdown('''
        The IZHI model is the fastest.
        Over three different current injection strengths mean Model speed was {0}
        ms, to find unkown rheoase value it takes {1} seconds'''.format(3.36,0.7,model_value))


      if model_value == "NEURONHH":
        st.markdown('''
        In the {2} Model:
        over three different current injection strengths mean Model speed was {0}
        ms, to find unkown rheoase value it takes {1} seconds'''.format(3.36,0.7,model_value))


 
      '''
      # Do you want to try again on a different model to see how that would look?
      '''

      another_go = st.radio("\
		  Want to keep model on screen and compare to new model?"
		  ,("No","Yes"))

      new_model_value = st.sidebar.radio("\
      Which models would you like to optimize"
      ,("ADEXP","IZHI","NEURONHH"))
      if another_go == "Yes" and (new_model_value is not model_value):
        instance_opt(experimental_constraints,MODEL_PARAMS,test_key,model_value,MU,NGEN)

