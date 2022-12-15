import argparse

import ga
import evaluator
import graph
import sys
import os
import math

from os import listdir
from os import path
from os.path import isfile, join

def parse_args():
    # capture the args with the parser
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-i', '--inst', dest='instance', type=str, required=True, help='path to problem instance')
    parser.add_argument('-k', dest='k_values', type=str, required=True, help='k number of tours')
    parser.add_argument('-s', '--seeds', dest='seeds', type=str, required=True, help='random seeds to run the ga')
    args = parser.parse_args()
    # check and adjust the parsed args
    args.instance = args.instance.replace(' ', '')
    if not path.exists(args.instance):
        sys.exit("Cannot find instance: " + args.instance)
    args.k_values = [int(i) for i in args.k_values.split(',')]
    args.seeds = [int(i) for i in args.seeds.split(',')]
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
        # create the evaluator
        evalor = evaluator.Evaluator(gph, k)
        evalor.depotNode = 0

        # create the genetic algorithm with the evaluator
        visualize_ga = True
        meta_ga = ga.GA(evalor, visualize_ga)
        meta_ga.init()

        # for every seed run the GA
        print('Running MetaGA with k=' + str(k))
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