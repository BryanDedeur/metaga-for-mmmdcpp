import ga
import evaluator
import graph
import sys
import os

from os import listdir
from os import path
from os.path import isfile, join

def testRouterHeuristic(gph):
    for i in range(1, 11):
        router = evaluator.Router(gph, i)
        router.buildToursWithSimpleHeuristic()
        router.save('results.csv')

def main():
    #benchmark_path = os.getcwd() + "/instances/custom-graphs/bryans/simple.csv"
    #benchmark_path = os.getcwd() + "/instances/ahrs-thesis/10A.dat"
    #benchmark_path = os.getcwd() + "/instances/stacs-graphs/graph-raw.csv"
    #benchmark_path = os.getcwd() + "/instances/bridge-instances/Warren-truss-bridge-4-segment.csv"
    #benchmark_path = os.getcwd() + "/instances/well-known-single-face-trusses/single-face-howe-truss-bridge-12-segment.json"
    benchmark_path = os.getcwd() + "/instances/ahrs-thesis"

    if not path.exists(benchmark_path):
        print("Cannot find benchmark path: ", benchmark_path)
        sys.exit()

    for filename in os.listdir(benchmark_path):

        # create the graph
        gph = graph.Graph(os.path.join(benchmark_path, filename))
        gph.SolveAndCacheShortestPaths()
        #gph.View(False)

        kValues = [8]
        seeds = [8115, 3520, 8647] # 9420, 3116, 6377, 6207, 4187, 3641, 8591, 3580, 8524, 2650, 2811, 9963, 7537, 3472, 3714, 8158, 7284, 6948, 6119, 5253, 5134, 7350, 2652, 9968, 3914, 6899, 4715]

        # run for all values of k
        for k in kValues:
            # create the evaluator
            evalator = evaluator.Evaluator(gph, k)
            evalator.depotNode = 0

            # create the genetic algorithm with the evaluator
            genAlg = ga.GA(evalator, True)
            genAlg.init()

            # for every seed run the GA
            print('Running GA with k=' + str(k))

            for seed in seeds:
                genAlg.run(seed)
                evalator.save('evalResults.txt')
                evalator.reset()

            print('overall best: ' + str(round(genAlg.getOverallBestObj(),2)))
            print('per seed average best: ' + str(round(genAlg.getAveSeedBestObj(),2)))
            print('per seed average num evaluations to achieve near best: ' + str(round(genAlg.getAveNumEvalsToAveBest(),2)))
            print('per seed reliability: ' + str(round(genAlg.getReliability(),2)))
            print('overall time: ' + str(round(genAlg.seedTimeStats.sum,2)) + 's')
        print()

if __name__ == '__main__':
    main()