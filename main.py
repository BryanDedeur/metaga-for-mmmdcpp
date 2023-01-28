import argparse

import ga
import evaluator
import graph
from router import Router
import sys
import os
import math
import options
import wandb

from os import listdir
from os import path
from os.path import isfile, join

def parse_args():
    # capture the args with the parser
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-i', '--inst', dest='instance', type=str, required=True, help='filepath to problem instance')
    parser.add_argument('-k', '--tours', dest='k_values', type=str, required=True, help='k number of tours. ex: -k 2,4,8')
    parser.add_argument('-d', '--depots', dest='depots', type=str, required=True, help='the deployment configuration (single, multi). ex: -d single')
    parser.add_argument('-s', '--seeds', dest='seeds', type=str, required=True, help='random seeds to run the ga. ex: -s 1234,3949')
    parser.add_argument('-j', '--heuristics', dest='heuristics', type=str, default='MMMR', required=False, help='the set of heuristics (MMMR, RR). ex: -j MMMR')
    args = parser.parse_args()

    # check and adjust the parsed args
    args.instance = args.instance.replace(' ', '')
    if not path.exists(args.instance):
        sys.exit("Cannot find instance: " + args.instance)
    args.k_values = [int(i) for i in args.k_values.split(',')]
    args.seeds = [int(i) for i in args.seeds.split(',')]
    args.heuristics = args.heuristics.replace(' ', '')
    args.depots = args.depots.replace(' ', '')
    return args

def main():
    # capturing the arguements
    args = parse_args()
    
    # create the graph
    gph = graph.Graph(args.instance)
    gph.solve_and_cache_shortest_paths()
    # gph.View(False)
    # TODO make sure to handle depots properly
    ga_options = options.Options()
    # run for all values of k
    for k in args.k_values:
        print('Configuring evaluator for k=' + str(k) + ' tours')

        # create a router for constructing tours
        router = Router(gph, k)
        depot = gph.size_v() - 1 # TODO fix for gdb instances
        for tour in router.tours:
            tour.depot = depot

        depots = []
        for tour in router.tours:
            depots.append(tour.depot)

        # create the evaluator
        evalor = evaluator.Evaluator(gph, k, router)
        evalor.depotNode = 0 # TODO make sure depot node is correct
        if args.heuristics == 'MMMR':
            evalor.geneLength = 2 # 4 total heuristics
            evalor.chromeLength = gph.size_e() * evalor.geneLength
            evalor.heuristics = [            
                router.add_edges_to_shortest_tour_with_min_cost_edge_from_nearest_unvisited_equidistant, # min cost
                router.add_edges_to_shortest_tour_with_mean_cost_edge_from_nearest_unvisited_equidistant, # median cost 
                router.add_edges_to_shortest_tour_with_mean_cost_edge_from_nearest_unvisited_equidistant, # max cost
                router.add_edges_to_shortest_tour_with_random_cost_edge_from_nearest_unvisited_equidistant # random cost 
            ]
        elif args.heuristics == 'RR':
            evalor.geneLength = len(bin(gph.maxVertexDegree)[2:])
            evalor.chromeLength = gph.size_e() * evalor.geneLength
            evalor.heuristics = []
            # the number of heuristics is dynamically changing based on the problem
            for i in range(pow(2,evalor.geneLength)): 
                evalor.heuristics.append(router.add_edges_to_shortest_tour_with_round_robin_nearest_unvisited_equidistant)

        # create the genetic algorithm with the evaluator
        meta_ga = ga.GA(evalor, ga_options)
        meta_ga.init()

        config = {
            'instance': gph.name,
            'k-value': k,
            'depots': [tour.depot for tour in router.tours],
            'heuristics': args.heuristics,
            'target runs': len(args.seeds),
            'ga': {
                'pop size': ga_options.populationSize,
                'num gens': ga_options.maxGen,
                'selection type': ga_options.selectionType,
                'crossover type': ga_options.crossType,
                'mutation type': ga_options.mutType,
                'p cross': ga_options.pCross,
                'p mutation': ga_options.pMut,
            }
        }

        def run_start(seed):
            wandb.init(project="meta-ga", name=str(seed), group="test1", config=config)
            return

        def run_end(seed, best_individual, run_time_elapsed):
            best_individual.evaluate()

            log_info = {
                'run best objective': best_individual.objective,
                'run best chromosome': str(best_individual),
                'run best solution': best_individual.solution,
                'run best sum tour costs': router.getSumTourLengths()
            }

            for i in range(len(router.tours)):
                log_info['run best tour'+str(i) + ' cost'] = router.tours[i].cost

            wandb.log(log_info)

            wandb.finish()
            return

        def generation_start(seed, gen):
            return

        def generation_end(seed, gen, best_individual, gen_time_elapsed, run_time_elapsed):
            # re-evaluate the best indivudal so router has all the right information
            best_individual.evaluate()

            log_info = {
                'gen best objective': meta_ga.population.objStats.min,
                'gen worst objective': meta_ga.population.objStats.max,
                'gen ave objective': meta_ga.population.objStats.mean(), 
                'gen duration(s)': gen_time_elapsed,
                'gen run time(s)': run_time_elapsed,
                'gen best sum tour costs': router.getSumTourLengths()
            }

            # capture data on wandb
            wandb.log(log_info)
            return

        meta_ga.on_run_start = run_start
        meta_ga.on_run_end = run_end
        meta_ga.on_generation_start = generation_start
        meta_ga.on_generation_end = generation_end

        # for every seed run the GA
        print('Running MetaGA on ' + str(len(args.seeds)) + ' seeds:')
        for seed in args.seeds:
            meta_ga.run(seed)
            evalor.save('results/eval_results.txt')
            # evalor.router.View()
            evalor.reset()

        # output the final results
        print('overall best: ' + str(round(meta_ga.getOverallBestObj(),2)))
        print('per seed average best: ' + str(round(meta_ga.getAveSeedBestObj(),2)))
        print('per seed average num evaluations to achieve near best: ' + str(round(meta_ga.getAveNumEvalsToAveBest(),2)))
        print('per seed reliability: ' + str(round(meta_ga.getReliability(),2)))
        print('overall time: ' + str(round(meta_ga.seedTimeStats.sum,2)) + 's')

if __name__ == '__main__':
    main()