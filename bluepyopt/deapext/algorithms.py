
"""Optimisation class"""

"""
Copyright (c) 2016, EPFL/Blue Brain Project

 This file is part of BluePyOpt <https://github.com/BlueBrain/BluePyOpt>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 021101301 USA.
"""

# pylint: disable=R0914, R0912


import random
import logging

import deap.algorithms
import deap.tools
import pickle

from tqdm.auto import tqdm

from .stoppingCriteria import MaxNGen
from deap.tools import cxSimulatedBinary
from deap import tools, gp
import random
import streamlit as st
import copy
logger = logging.getLogger('__main__')
DASK = False
import dask

import numpy as np
import streamlit as st
def _evaluate_invalid_fitness(toolbox, population):
    '''Evaluate the individuals with an invalid fitness

    Returns the count of individuals with invalid fitness
    '''
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    eval_ = toolbox.evaluate
    fitnesses = toolbox.map(eval_, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    return len(invalid_ind)


def _update_history_and_hof(halloffame, history, population):
    '''Update the hall of fame with the generated individuals

    Note: History and HallofFame behave like dictionaries
    '''
    if halloffame is not None:
        halloffame.update(population)

    history.update(population)


def _record_stats(stats, logbook, gen, population, invalid_count,cleanse_sins=True):
    '''Update the statistics with the new population'''

    if cleanse_sins:
        pop2 = copy.copy(population)
        for i,p in enumerate(pop2):
            remove = False
            for f in p.fitness.values:
                if f==1000:
                    remove = True
            if remove:
                del pop2[i]
        record = stats.compile(pop2) if stats is not None else {}
    else:

        record = stats.compile(population) if stats is not None else {}

    logbook.record(gen=gen, nevals=invalid_count, **record)



def _get_offspring(NGEN,parents, toolbox, cxpb, mutpb, mu, wild=False):
    # Register the mate operator
    #print(dir(toolbox.mutate.args))
    #print(dir(toolbox.variate.args))

    #import pdb
    #pdb.set_trace()
    '''
    ETA = 5
    toolbox.register(
        "mate",
        deap.tools.cxSimulatedBinaryBounded,
        eta=ETA/NGEN,
        low=LOWER,
        up=UPPER)

    # Register the mutation operator
    toolbox.register(
        "mutate",
        deap.tools.mutPolynomialBounded,
        eta=ETA/NGEN,
        low=LOWER,
        up=UPPER,
        indpb=0.5)

    # Register the variate operator
    toolbox.register("variate", deap.algorithms.varAnd)
    '''
    children = deap.algorithms.varOr(parents, toolbox, int(mu), cxpb, mutpb)

    #children = toolbox.variate(parents, int(mu), cxpb, mutpb)
    for chromosome in children:
        for gene in chromosome:
            try:
                assert not np.isnan(gene)
            except:
                print(np.isnan(gene),gene)
    # TODO restore time varying eta

    #if hasattr(toolbox, 'variate'):
    #    return toolbox.variate(parents, toolbox, cxpb, mutpb)
    #else:
    #    return deap.algorithms.varAnd(parents, toolbox, cxpb, mutpb)


    #if hasattr(toolbox, 'variate'):
    #    return toolbox.variate(parents, toolbox, cxpb, mutpb)
    return children

    '''return the offsprint, use toolbox.variate if possible'''
    '''
    if wild:
        parents = toolbox.clone(parents)

        children = []
        for ind1,ind2 in zip(parents[1:1],parents[0:2]):
            op_choice = random.random()
            if random.random() < cxpb:
                #if op_choice < cxpb:

                lower = toolbox.uniformparams.args[0][0]
                upper = toolbox.uniformparams.args[1][0]
                ind3 = tools.cxSimulatedBinaryBounded(ind1, ind2, 0.75,lower,upper)
                #gp.cxOnePointLeafBiased(ind1, ind2, 0.9)
                try:
                    del ind3[0].fitness.values #= False
                    del ind3[1].fitness.values # = False
                except:
                    pass
                children.append(ind3[0])
                children.append(ind3[1])
    else:
    '''
    '''
    children = []
    for ind1,ind2 in zip(parents[1:1],parents[0:2]):
        lower = toolbox.uniformparams.args[0][0]
        upper = toolbox.uniformparams.args[1][0]
        ind3 = tools.cxSimulatedBinaryBounded(ind1, ind2, 0.9,lower,upper)
        try:
            del ind3[0].fitness.values #= False
            del ind3[1].fitness.values # = False
        except:
            pass
        children.append(ind3[0])
        children.append(ind3[1])
    '''

    #lambda_ = mu

    #children = deap.algorithms.varAnd(parents, toolbox, cxpb, mutpb)

    #if hasattr(toolbox, 'variate'):
    #    return toolbox.variate(parents, toolbox, cxpb, mutpb)


def _check_stopping_criteria(criteria, params):
    for c in criteria:
        c.check(params)
        if c.criteria_met:
            logger.info('Run stopped because of stopping criteria: ' +
                        c.name)
            return True
    else:
        return False

def clean_record(population):
    pop2 = copy.copy(population)

    cnt=0
    for i,p in enumerate(pop2):
        remove = False
        for f in p.fitness.values:
            if f==1000:
                remove = True
        if remove:
            del pop2[i]
            cnt+=1
    for i,p in enumerate(pop2):
        if cnt>0:
            pop2.append(pop2[i])
            cnt-=1


    del population
    population = pop2
    return population
def eaAlphaMuPlusLambdaCheckpoint(
        population,
        toolbox,
        mu,
        cxpb,
        mutpb,
        ngen,
        stats=None,
        halloffame=None,
        cp_frequency=1,
        cp_filename=None,
        continue_cp=False,
        extra=None,
        ELITISM=True):
    r"""This is the :math:`(~\alpha,\mu~,~\lambda)` evolutionary algorithm

    Args:
        population(list of deap Individuals)
        toolbox(deap Toolbox)
        mu(int): Total parent population size of EA
        cxpb(float): Crossover probability
        mutpb(float): Mutation probability
        ngen(int): Total number of generation to run
        stats(deap.tools.Statistics): generation of statistics
        halloffame(deap.tools.HallOfFame): hall of fame
        cp_frequency(int): generations between checkpoints
        cp_filename(string): path to checkpoint filename
        continue_cp(bool): whether to continue
    """

    if continue_cp:
        # A file name has been given, then load the data from the file
        cp = pickle.load(open(cp_filename, "rb"))
        population = cp["population"]
        parents = cp["parents"]
        start_gen = cp["generation"]
        halloffame = cp["halloffame"]
        logbook = cp["logbook"]
        history = cp["history"]
        random.setstate(cp["rndstate"])
    else:
        best_vs_gen = []
        prog_bar = st.progress(0)

        # Start a new evolution
        start_gen = 1
        parents = population[:]
        logbook = deap.tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
        history = deap.tools.History()

        # TODO this first loop should be not be repeated !
        invalid_count = _evaluate_invalid_fitness(toolbox, population)
        _update_history_and_hof(halloffame, history, population)
        _record_stats(stats, logbook, start_gen, population, invalid_count)
        logger.info(logbook.stream)


    stopping_criteria = [MaxNGen(ngen)]

    # Begin the generational process
    gen = start_gen + 1
    stopping_params = {"gen": gen}

    pbar = tqdm(total=ngen)
    while not(_check_stopping_criteria(stopping_criteria, stopping_params)):
        offspring = _get_offspring(ngen, parents, toolbox, cxpb, mutpb, int(mu))
        offspring = clean_record(offspring)

        population = parents + offspring
        population.append(halloffame[0])

        flo = np.sum(halloffame[0].fitness.values)
        stopping_params.update({'hof':flo})
        stop = _check_stopping_criteria(stopping_criteria, stopping_params)

        invalid_count = _evaluate_invalid_fitness(toolbox, offspring)

        _update_history_and_hof(halloffame, history, population)

        ##
        # Throw away unfit genes
        ##
        #print(toolbox.select)

        parents = toolbox.select(population, int(mu/5))

        parents = clean_record(parents)
        population = clean_record(population)

        _record_stats(stats, logbook, gen, population, invalid_count)

        logger.info(logbook.stream)

        if(cp_filename and cp_frequency and
           gen % cp_frequency == 0 or cp_filename and stop):
            cp = dict(population=population,
                      generation=gen,
                      parents=parents,
                      halloffame=halloffame,
                      history=history,
                      logbook=logbook,
                      rndstate=random.getstate())
            pickle.dump(cp, open(cp_filename, "wb"))
            logger.debug('Wrote checkpoint to %s', cp_filename)
        current_prog = gen / ngen
        prog_bar.progress(current_prog)

        gen += 1
        stopping_params["gen"] = gen
        pbar.update(1)
    pbar.update(1)
    pbar.close()
    cp = dict(population=population,
            generation=gen,
            parents=parents,
            halloffame=halloffame,
            history=history,
            logbook=logbook,
            rndstate=random.getstate())
    #with open('out_file.p', "wb") as f:
    #    pickle.dump(cp, f)

    return population, halloffame, logbook, history
