import ga
import evaluator
import graph
import sys
import os
import math

from os import listdir
from os import path
from os.path import isfile, join

def main():
    # capture the arguements
    args = sys.argv
    
    # read the arguments
    problemInstancePath = ""
    kValues = []
    seeds = []

    if len(args) > 1:
        problemInstancePath = args[1]
        if len(args) > 2:
            kValueString = args[2]
            tokens = kValueString.split(",")
            kValues = [int(i) for i in tokens]
            if len(args) > 3:
                seedsString = args[3]
                tokens = seedsString.split(",")
                seeds = [int(i) for i in tokens]

    if not path.exists(problemInstancePath):
        print("Cannot find problem instance with path: ", problemInstancePath)
        sys.exit()

    # create the graph
    gph = graph.Graph(problemInstancePath)
    gph.SolveAndCacheShortestPaths()
    # gph.View(False)

    # run for all values of k
    for k in kValues:
        # create the evaluator
        evalor = evaluator.Evaluator(gph, k)
        evalor.depotNode = 0

        # create the genetic algorithm with the evaluator
        visualize_ga = False
        meta_ga = ga.GA(evalor, visualize_ga)
        meta_ga.init()

        # for every seed run the GA
        print('Running MetaGA with k=' + str(k))
        for seed in seeds:
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