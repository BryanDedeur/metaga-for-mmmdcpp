
import random
import evaluator
import sys
import subprocess
import options
import matplotlib.pyplot as plt
import numpy as np
import statistics
import os

from individual import Individual
from evaluator import Evaluator
from population import Population
from timeit import default_timer as timer
from multiprocessing import Process, Pool, Queue, TimeoutError, process

class GA:
	def __init__(self, evaler, visualize):
		self.version = 3.0
		self.options = options.Options()

		self.runCount = 0

		# self.minFitness = float('inf')
		# self.maxFitness = 0
		# self.maxObjective = 0
		self.eval = evaler

		self.population = Population(self)
		self.bestIndividual = Individual(self)

		# statistics data
		self.genMinFitStats = []
		self.genAveFitStats = []
		self.genMaxFitStats = []
		self.genMinObjStats = []
		self.genAveObjStats = []
		self.genMaxObjStats = []
		self.genMinTimeStats = []
		self.genAveTimeStats = []
		self.genMaxTimeStats = []

		# y axis data for plotting lines
		self.aveMinFitData = []
		self.aveAveFitData = []
		self.aveMaxFitData = []
		self.aveMinObjData = []
		self.aveAveObjData = []
		self.aveMaxObjData = []
		self.aveMinTimeData = []
		self.aveAveTimeData = []
		self.aveMaxTimeData = []

		self.objAnnotation = None

		self.seedBestObjStats = statistics.Statistics()
		self.seedTimeStats = statistics.Statistics()

		# annotations
		self.fitAnnotation = None

		# visualization
		self.fitLines = []
		self.objLines = []
		self.timeLines = []

		# self.visualize = visualize
		# self.createVisuals()
		# if visualize:
		# 	plt.ion()
		# 	self.show()

		# parallelization
		self.processEvaluators = []
		self.evaluationQueue = Queue()
		self.resultQueue = Queue()

	# allocates memory for the genetic algorithm
	def init(self):
		self.population.init()
		self.bestIndividual.init()
		for g in range(self.options.maxGen):
			self.genMinFitStats.append(statistics.Statistics())
			self.genAveFitStats.append(statistics.Statistics())
			self.genMaxFitStats.append(statistics.Statistics())
			self.genMinObjStats.append(statistics.Statistics())
			self.genAveObjStats.append(statistics.Statistics())
			self.genMaxObjStats.append(statistics.Statistics())
			self.genMinTimeStats.append(statistics.Statistics())
			self.genAveTimeStats.append(statistics.Statistics())
			self.genMaxTimeStats.append(statistics.Statistics())
			self.aveMinFitData.append(0)
			self.aveAveFitData.append(0)
			self.aveMaxFitData.append(0)
			self.aveMinObjData.append(0)
			self.aveAveObjData.append(0)
			self.aveMaxObjData.append(0)
			self.aveMinTimeData.append(0)
			self.aveAveTimeData.append(0)
			self.aveMaxTimeData.append(0)

    # Deleting (Calling destructor)
	def __del__(self):
		# end all multi threaded processes
		for c in range(len(self.processEvaluators)):
			self.processEvaluators[c].join()

	def listenForEvaluationRequests(self, evaluator, evalQueue, resultQueue):
		while True:
			message = evalQueue.get()
			if message != None:
				if message == 'DONE':
					print("DONE")
					break
				else:
					print(message)

	def resetStatistics(self):
		# TODO this does not work properly
		self.fitStats.clear()
		self.objStats.clear()
		self.timeStats.clear()

	def genStatistics(self, population, gen):
		# store the fitness, objective, time stats for each generation
		self.genMinFitStats[gen].addValue(population.fitStats.min)
		self.genAveFitStats[gen].addValue(population.fitStats.mean())
		self.genMaxFitStats[gen].addValue(population.fitStats.max)
		self.genMinObjStats[gen].addValue(population.objStats.min)
		self.genAveObjStats[gen].addValue(population.objStats.mean())
		self.genMaxObjStats[gen].addValue(population.objStats.max)
		self.genMinTimeStats[gen].addValue(population.timeStats.min)
		self.genAveTimeStats[gen].addValue(population.timeStats.mean())
		self.genMaxTimeStats[gen].addValue(population.timeStats.max)
		# update the average of averages of all seeds
		self.aveMinFitData[gen] = self.genMinFitStats[gen].mean()
		self.aveAveFitData[gen] = self.genAveFitStats[gen].mean()
		self.aveMaxFitData[gen] = self.genMaxFitStats[gen].mean()
		self.aveMinObjData[gen] = self.genMinObjStats[gen].mean()
		self.aveAveObjData[gen] = self.genAveObjStats[gen].mean()
		self.aveMaxObjData[gen] = self.genMaxObjStats[gen].mean()
		self.aveMinTimeData[gen] = self.genMinTimeStats[gen].mean()
		self.aveAveTimeData[gen] = self.genAveTimeStats[gen].mean()
		self.aveMaxTimeData[gen] = self.genMaxTimeStats[gen].mean()
		# store the best over all seeds
		if population.bestIndividual.fitness > self.bestIndividual.fitness:
			self.bestIndividual.copy(population.bestIndividual)
		
	def setSeed(self, seed):
		random.seed(seed)
		self.population.setSeed(seed)
		self.eval.setSeed(seed)
		self.seed = seed

	def getOverallBestObj(self):
		return self.bestIndividual.objective

	def getAveSeedBestObj(self):
		return self.seedBestObjStats.mean()

	def getAveNumEvalsToAveBest(self):
		aveBest = self.getAveSeedBestObj()
		for i in range(len(self.aveMinObjData)):
			if self.aveMinObjData[i] <= aveBest:
				return i * self.options.populationSize
	
	def getReliability(self):
		# num seeds that acheive average seed best
		numSeeds = 0
		aveBest = self.getAveSeedBestObj()
		for s in range(self.runCount):
			for g in range(self.options.maxGen):
				if self.aveMinObjData[g] <= aveBest:
					numSeeds += 1
					break
		return numSeeds / self.runCount
	

	def run(self, seed = 0):
		# set the seed
		self.setSeed(seed)
		start = timer()
		# console output run status
		print(str(self.runCount + 1) + '. GA evolving on seed (' + str(self.seed) + '): [', end = '')
		bestSeedObj = float('inf')
		for	gen in range(self.options.maxGen):
			if gen == 0:
				# randomize population with whatever seed is set
				self.population.randomize(0, self.population.sizeParents())
			else:
				# regenerate new population
				self.population.generate()

			if (gen % int(self.options.maxGen * 0.05) == 0):
				print('.', end = '')

			# if the final generation
			if gen == (self.options.maxGen - 1):
				# write the individuals result chromosome to a file
				f = open("final_population_chromosomes.csv", "a")
				f.write("seed: " + str(self.seed) + "\n")
				for i in range(0, int(len(self.population.individuals) / 2)):
					individual = self.population.individuals[i]
					out = ""
					for j in range(len(individual.result_heursitics_used)):
						out += str(individual.result_heursitics_used[j]) + ","
					out += "\n"
					f.write(out)
				f.close()

			
			# gather statistics and visualize
			self.genStatistics(self.population, gen)
			# self.updateVisuals(gen)

			# get the best objective value
			if self.population.bestIndividual.objective < bestSeedObj:
				bestSeedObj = self.population.bestIndividual.objective

		self.seedBestObjStats.addValue(bestSeedObj)
		self.seedTimeStats.addValue(timer()-start)
		# console output end of run
		print('] in ' + str(round(timer()-start,3)) + 's')
		self.runCount += 1

	def createVisuals(self):
		self.figure, self.axes  = plt.subplots(3)

		xvalues = np.linspace(0, self.options.maxGen, self.options.maxGen)
		yvalues = np.linspace(0, 0, self.options.maxGen)

		for i in range(3):
			if i == 0:
				style = 'b-'
				label = 'min'
			elif i == 1:
				style = 'g-'
				label = 'ave'
			elif i == 2:
				style = 'r-'
				label = 'max'
			self.fitLines.append(self.axes[0].plot(xvalues, yvalues, style)[0])
			self.objLines.append(self.axes[1].plot(xvalues, yvalues, style)[0])
			self.timeLines.append(self.axes[2].plot(xvalues, yvalues, style)[0])
		
		self.axes[0].set_title('ave seed ave generation k=' + str(len(self.eval.router.tours)) + ' results ' + self.eval.GetProblemName())
		self.axes[0].set_ylabel('Fitness')

		# self.axes[1].set_xlabel('Generation')
		self.axes[1].set_ylabel('Objective')
		self.objAnnotation = self.axes[1].annotate('NICE', (0.5,0.5))

		self.axes[2].set_xlabel('Generation')
		self.axes[2].set_ylabel('Time')

	def updateVisuals(self, gen):
		# set the y data on all the lines
		self.fitLines[0].set_ydata(self.aveMinFitData)
		self.fitLines[1].set_ydata(self.aveAveFitData)
		self.fitLines[2].set_ydata(self.aveMaxFitData)
		self.objLines[0].set_ydata(self.aveMinObjData)
		self.objLines[1].set_ydata(self.aveAveObjData)
		self.objLines[2].set_ydata(self.aveMaxObjData)
		self.timeLines[0].set_ydata(self.aveMinTimeData)
		self.timeLines[1].set_ydata(self.aveAveTimeData)
		self.timeLines[2].set_ydata(self.aveMaxTimeData)

		# resize the plots
		if gen != 0:
			genLim = gen
			if self.runCount > 0:
				genLim = self.options.maxGen
			offsetPercentage = 0.05
			minValue = min(self.aveMinFitData[:genLim])
			maxValue = max(self.aveMaxFitData[:genLim])
			minMaxRange = maxValue - minValue
			self.axes[0].set_ylim(minValue - (offsetPercentage * minMaxRange), maxValue + (offsetPercentage * minMaxRange))

			minValue = min(self.aveMinObjData[:genLim])
			maxValue = max(self.aveMaxObjData[:genLim])
			minMaxRange = maxValue - minValue
			self.axes[1].set_ylim(minValue - (offsetPercentage * minMaxRange), maxValue + (offsetPercentage * minMaxRange))
			if minMaxRange == 0:
				self.axes[1].set_yticks(np.arange(minValue, maxValue, 1))
			else:
				self.axes[1].set_yticks(np.arange(minValue, maxValue, round(minMaxRange)*.2))

			minValue = min(self.aveMinTimeData[:genLim])
			maxValue = max(self.aveMaxTimeData[:genLim])
			minMaxRange = maxValue - minValue
			self.axes[2].set_ylim(minValue - (offsetPercentage * minMaxRange), maxValue + (offsetPercentage * minMaxRange))

		# update visuals
		self.figure.canvas.draw()
		self.figure.canvas.flush_events()

	def getHeaderString(self, delim = ',', ending = '\n'):
		return (
			 'version' + delim +
			 'runs' + delim +
			 'pop size' + delim +
			 'num gens' + delim +
			 'selection' + delim +
			 'cross' + delim +
			 'p-cross' + delim +
			 'mutate' + delim +
			 'p-mutate' + ending
		 )

	def to_string(self, delimiter = ',', ending = '\n'):
		data = [
			self.version,
			self.runCount,
			self.options.populationSize,
			self.options.selectionType,
			self.options.crossType,
			self.options.pCross,
			self.options.mutType,
			self.options.pMut,
			]
		formatted = ''
		for i in range(len(data)):
			formatted += str(data[i])
			if i < len(data) - 1:
				formatted += delimiter
			else:
				formatted += ending
		return formatted

	def save(self):
		# results
		resultsPath = os.getcwd() + self.options.resultsDir + self.options.resultsFile
		print("Saving results to: " + resultsPath)

		resultsFile = open(resultsPath, "a") 
		if os.path.exists(resultsPath) and os.stat(resultsPath).st_size == 0:
			resultsFile.write(self.getHeaderString('\t', '\n'))
		resultsFile.write(self.to_string('\t', '\n'))
		resultsFile.close()

		# visuals
		self.plotData()
		visualsPath = os.getcwd() + self.options.resultsDir + self.eval.problem.name + '.png'
		self.figure.savefig(visualsPath)

	def show(self, blocking = False):
		#print("SHOWING")
		plt.show(block=blocking)
		return