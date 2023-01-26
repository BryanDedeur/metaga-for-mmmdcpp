import argparse

import ga
import evaluator
import graph
from router import Router
import sys
import os
import math

from os import listdir
from os import path
from os.path import isfile, join

def parse_args():
    # capture the args with the parser
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-i', '--inst', dest='instance', type=str, required=True, help='filepath to problem instance')
    parser.add_argument('-k', '--tours', dest='k_values', type=str, required=True, help='k number of tours. ex: -k 2,4,8')
    parser.add_argument('-md', '--multi_depot', dest='multi_depot_routing', type=bool, default=False, required=False, help='build tours using multiple depots')
    parser.add_argument('-s', '--seeds', dest='seeds', type=str, required=True, help='random seeds to run the ga. ex: -s 1234,3949')
    parser.add_argument('-j', '--heuristics', dest='heuristics', type=str, default='MAMR', required=False, help='the set of heuristics (MAMR, RR). ex: -j MAMR')

    args = parser.parse_args()
    # check and adjust the parsed args
    args.instance = args.instance.replace(' ', '')
    if not path.exists(args.instance):
        sys.exit("Cannot find instance: " + args.instance)
    args.k_values = [int(i) for i in args.k_values.split(',')]
    args.seeds = [int(i) for i in args.seeds.split(',')]
    args.heuristics = args.heuristics.replace(' ', '')
    return args

def main():
    # capturing the arguements
    args = parse_args()
    
    # create the graph
    gph = graph.Graph(args.instance)
    gph.solve_and_cache_shortest_paths()
    # gph.View(False)

    # run for all values of k
    for k in args.k_values:
        print('Configuring evaluator for k=' + str(k) + ' tours')

        # create a router for constructing tours
        router = Router(gph, k)

        # create the evaluator
        evalor = evaluator.Evaluator(gph, k, router)
        evalor.depotNode = 0 # TODO make sure depot node is correct
        if args.heuristics == 'MAMR':
            evalor.geneLength = 2 # 4 total heuristics
            evalor.chromeLength = gph.size_e() * evalor.geneLength
            evalor.heuristics = [            
                    router.findLowestCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges, # min cost
                    router.findMidCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges, # ave cost 
                    router.findHighestCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges, # max cost
                    router.findRandomCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges # random cost 
                ]
        elif args.heuristics == 'RR':
            evalor.geneLength = len(bin(gph.maxVertexDegree)[2:])
            evalor.chromeLength = gph.size_e() * evalor.geneLength

        # create the genetic algorithm with the evaluator
        visualize_ga = False
        meta_ga = ga.GA(evalor, visualize_ga)
        meta_ga.init()

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