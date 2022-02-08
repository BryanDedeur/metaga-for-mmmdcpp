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
    seeds = [] # 8115, 3520, 8647, 9420, 3116, 6377, 6207, 4187, 3641, 8591, 3580, 8524, 2650, 2811, 9963, 7537, 3472, 3714, 8158, 7284, 6948, 6119, 5253, 5134, 7350, 2652, 9968, 3914, 6899, 4715]

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
    #gph.View(False)

    # # run for all values of k
    for k in kValues:
        # for k_i in range(k):
        #     k_depot = gph.SizeV() - (k_i - (math.floor(k_i/4)*4)) - 1
        #     print("K(" + str(k_i) + ") robot will deploy at " + str(k_depot))

        # create the evaluator
        evalator = evaluator.Evaluator(gph, k)

        # create the genetic algorithm with the evaluator
        genAlg = ga.GA(evalator, True)
        genAlg.init()

        # for every seed run the GA
        print('Running GA with k=' + str(k))

        for seed in seeds:
            genAlg.run(seed)
            evalator.save('evalResults.txt')
            #evalator.router.View()
            evalator.reset()

        print('overall best: ' + str(round(genAlg.getOverallBestObj(),2)))
        print('per seed average best: ' + str(round(genAlg.getAveSeedBestObj(),2)))
        print('per seed average num evaluations to achieve near best: ' + str(round(genAlg.getAveNumEvalsToAveBest(),2)))
        print('per seed reliability: ' + str(round(genAlg.getReliability(),2)))
        print('overall time: ' + str(round(genAlg.seedTimeStats.sum,2)) + 's')

if __name__ == '__main__':
    main()