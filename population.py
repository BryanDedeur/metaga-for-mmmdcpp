import multiprocessing
import evaluator
import random
import statistics
import os

from multiprocessing import Process, Pool, Queue, TimeoutError, process
from os import stat
from individual import Individual
from options import CrossoverType

class Population(object):
	def	__init__(self, geneticAlgorithm):
		self.ga = geneticAlgorithm
		self.options = geneticAlgorithm.options
		self.eval = geneticAlgorithm.eval

		self.individuals = [] 
		self.bestIndividual = None
		self.seed = 0

		self.fitStats = statistics.Statistics()
		self.objStats = statistics.Statistics()
		self.timeStats = statistics.Statistics()

		self.sumScaledFitness = 0

	def data_str(self, prefix = ''):
		pop_str = ''
		for i in range(self.size_parents()):
			pop_str += prefix + str(i) + ',' + self.individuals[i].data_str() + '\n'
		return pop_str

	def init(self):
		"""Allocates memory for the population"""
		self.individuals = [] 
		# initialize population with randomly generated Individuals
		for i in range(self.options.populationSize * self.options.chcLambda):
			self.individuals.append(Individual(self))
			self.individuals[i].init()

	def size(self):
		return len(self.individuals)
	
	def size_parents(self):
		return int(self.size() / 2)

	def setSeed(self, seed):
		random.seed(seed)
		self.seed = seed
		for individual in self.individuals:
			individual.setSeed(seed)
	
	def resetStatistics(self):
		self.fitStats.clear()
		self.objStats.clear()
		self.timeStats.clear()
		self.bestIndividual = None

	def addIndividualStatistics(self, individual):
		self.fitStats.addValue(individual.fitness)
		self.objStats.addValue(individual.objective)
		self.timeStats.addValue(individual.evalTime)
		if self.bestIndividual == None:
			self.bestIndividual = individual
		elif individual.fitness > self.bestIndividual.fitness:
			self.bestIndividual = individual

	def scaleFitnessLinearly(self, start: int, end: int):
		Copies = 1.2 # any desired value 1.2 has worked well
		scaleUp = 1000000
		fmin = self.fitStats.min * scaleUp
		fmax = self.fitStats.max * scaleUp
		fave = self.fitStats.mean() * scaleUp

		a = 0
		b = 0
		if fmin > ((Copies * fave) - fmax) / (Copies - 1):
			a = (fave * (Copies - 1)) / (fmax - fave)
			b = ((fmax - (Copies * fave)) * fave) / (fmax - fave)
		else:
			Copies = 2
			if (fmax - fave != 0):
				a = fave / (fmax - fave)
				b = (-fave * fmin) / (fmax - fave)

		# apply the new fitness to each individual
		# reset the sum fitness tracker
		self.sumScaledFitness = 0
		for i in range(start, end):
			self.individuals[i].scaledFitness = a * (self.individuals[i].fitness * scaleUp) + b
			self.sumScaledFitness += (self.individuals[i].scaledFitness)
			#print(str(self.individuals[i].scaledFitness) + ' = ' + '(' + str(a) + ')' + str(self.individuals[i].fitness * scaleUp) + ' + ' + str(b))
			#if (self.individuals[i].scaledFitness < 0):
				#print("Our fitness scaling resulted in a negative number. This might be a problem!")

	def randomize(self, start: int, end: int):
		self.resetStatistics()
		# randomize the population
		for i in range(start, end):
			self.individuals[i].randomize()
			self.addIndividualStatistics(self.individuals[i])

	def select(self, start: int, end: int, useScaledFitness = False):
		# roulette wheel selection
		randFraction = 0
		if useScaledFitness:
			randFraction = self.sumScaledFitness * random.random()
		else:
			randFraction = self.fitStats.sum * random.random()
		sum = 0
		i = 0
		for i in range(start, end): 
			ind = self.individuals[i]
			if useScaledFitness:
				sum += ind.scaledFitness
			else:
				sum += ind.fitness
			if randFraction <= sum:
				return ind
		print("Selection failed, we went out of fitness bounds")
		return None

	def selectPair(self, start: int, end: int, useScaledFitness = False):
		i1 = self.select(start, end, useScaledFitness)
		i2 = self.select(start, end, useScaledFitness)
		return (i1, i2)

	def crossover1Point(self, parent1, parent2, ancestor1, ancestor2):
		# children takeover the ancestors
		child1 = ancestor1
		child2 = ancestor2
		# set initial crossover point outside of bounds of chromosome
		xp = self.eval.chromeLength
		# determine if should crossover
		if random.random() < self.options.pCross:
			xp = random.randint(1, self.eval.chromeLength)
		# clone parent genetic information
		for i in range(0, self.eval.chromeLength):
			if i < xp:
				child1.chromosome[i] = parent1.chromosome[i]
				child2.chromosome[i] = parent2.chromosome[i]
			else:
				child1.chromosome[i] = parent2.chromosome[i]
				child2.chromosome[i] = parent1.chromosome[i]
		return (child1, child2)

	def crossover2Point(self, parent1, parent2, ancestor1, ancestor2):
		# children takeover the ancestors
		child1 = ancestor1
		child2 = ancestor2
		# set initial crossover point outside of bounds of chromosome
		xp1 = self.eval.chromeLength
		xp2 = self.eval.chromeLength

		# determine if should crossover
		if random.random() < self.options.pCross:
			tempxp1 = random.randint(1, self.eval.chromeLength)
			tempxp2 = random.randint(1, self.eval.chromeLength)
			xp1 = min(tempxp1, tempxp2)
			xp2 = max(tempxp1, tempxp2)

		# clone parent genetic information
		for i in range(0, self.eval.chromeLength):
			if i < xp1:
				child1.chromosome[i] = parent1.chromosome[i]
				child2.chromosome[i] = parent2.chromosome[i]
			elif i < xp2:
				child1.chromosome[i] = parent2.chromosome[i]
				child2.chromosome[i] = parent1.chromosome[i]
			else:
				child1.chromosome[i] = parent1.chromosome[i]
				child2.chromosome[i] = parent2.chromosome[i]
		return (child1, child2)

	def crossoverUniform(self, parent1, parent2, ancestor1, ancestor2):
		# children takeover the ancestors
		child1 = ancestor1
		child2 = ancestor2
		
		# determine if crossover should even happen
		if random.random() < self.options.pCross:
			# use probability to determine how much information is exchanged
			probOfExchange = 0.5
			for i in range(0, self.eval.chromeLength):
				if random.random() < probOfExchange: 
					child1.chromosome[i] = parent1.chromosome[i]
					child2.chromosome[i] = parent2.chromosome[i]
				else:
					child1.chromosome[i] = parent2.chromosome[i]
					child2.chromosome[i] = parent1.chromosome[i]
		else:
			# clone the parent information directly over
			for i in range(0, self.eval.chromeLength):
				child1.chromosome[i] = parent1.chromosome[i]
				child2.chromosome[i] = parent2.chromosome[i]
		return (child1, child2)

	def crossoverPair(self, parent1, parent2, ancestor1, ancestor2):
		# determine which crossover method to use
		if self.ga.options.crossType == CrossoverType.OnePoint:
			return self.crossover1Point(parent1, parent2, ancestor1, ancestor2)
		elif self.ga.options.crossType == CrossoverType.TwoPoint:
			return self.crossover2Point(parent1, parent2, ancestor1, ancestor2)
		elif self.ga.options.crossType == CrossoverType.Uniform:
			return self.crossoverUniform(parent1, parent2, ancestor1, ancestor2)

	def mutatePair(self, child1, child2):
		child1.mutate()
		child2.mutate()
	
	def evaluatePair(self, child1, child2):
		child1.evaluate()
		child2.evaluate()

	def comparator(self, individual):
		return individual.fitness

	# def stringToFitness(self, data):
	# 	evalObj = evaluator.Evaluator(self.eval.graph, self.eval.numTours)
	# 	self.individuals[id].evaluate(evalObj)

	def evaluationProcess(self, evaluator, start, end):
		results = []
		for i in range(start, end):
			results.append(self.individuals[i].evaluate(evaluator, i))

		return results
		
	# evaluates the whole population or a subset of the population with multi threading
	def evaluateInParallel(self, start = 0, end=0):
		# create evaluator processes on all cores
		numProcesses = os.cpu_count()
		results = []

		# create a multiprocessing pool
		pool = multiprocessing.Pool(numProcesses)

		numGroups = numProcesses
		groupSize = int((end - start) / numGroups)

		begin = start
		for p in range(numProcesses):
			last = end
			if p != numProcesses - 1:
				last = begin + groupSize - 1
			results.append(pool.apply_async(self.evaluationProcess, (self.processEvaluators[p],begin,last)))
			begin += groupSize

		pool.close()
		pool.join()

		for processResults in results:
			for indiviudalResult in processResults.get():
				self.individuals[indiviudalResult[3]].fitness = indiviudalResult[0]
				self.individuals[indiviudalResult[3]].objective = indiviudalResult[1]
				self.individuals[indiviudalResult[3]].evalTime = indiviudalResult[2]

	def evaluateInParallel2(self, start = 0, end = 0):
		# add all the requests to the queue
		for i in range(start, end):
			self.ga.evaluationQueue.put("HI from " + str(i))
		self.ga.evaluationQueue.put("DONE")

	def regenerate(self):
		# scale parent and child population
		if self.ga.options.linearFitnessScaling:
			self.scaleFitnessLinearly(0, self.size_parents())

		# generate new population
		for i in range(0, self.size_parents(), 2):
			# select two individuals
			parents = self.selectPair(0, self.size_parents(), self.ga.options.linearFitnessScaling)

			# get ancestors to replace
			a1 = self.individuals[i + self.size_parents()]
			a2 = self.individuals[i + self.size_parents() + 1]

			# crossover two individuals to produce children in ancestor slots
			children = self.crossoverPair(parents[0], parents[1], a1, a2)

			# mutate two new children individuals
			self.mutatePair(children[0], children[1])

			# evaluate two new children
			self.evaluatePair(children[0], children[1])

		#self.evaluateInParallel(self.size_parents(), self.size())

		for i in range(self.size_parents(), self.size()):
			# add children statistics
			self.addIndividualStatistics(children[0])
			self.addIndividualStatistics(children[1])

		# if CHC sort population
		self.individuals.sort(key = self.comparator, reverse = True)

		# else swap children and parent slots

		# recompute statistics only considering new parent population
		self.resetStatistics()
		for i in range(0, self.size_parents()):
			self.addIndividualStatistics(self.individuals[i])