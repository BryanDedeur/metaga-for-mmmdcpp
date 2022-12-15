import random
import evaluator

class Individual:
	def __init__(self, population):
		self.population = population
		self.options = population.options
		self.eval = population.eval

		self.chromosome = []
		self.chromosomeLength = self.eval.chromeLength

		self.solution = ''

		self.fitness = 0
		self.objective = 0
		self.evalTime = 0

		self.scaledFitness = 0
	
	def __str__(self):
		"""Returns chromosome as string"""
		chrom_str = ''
		for i in self.chromosome:
			chrom_str += str(i)
		return chrom_str

	def data_str(self, prefix = '', precision = 6):
		"""Returns fitness, objective, and evaluation time as a string
		@param prefix text to add before the string
		@param precision number of decimal places
		"""
		return prefix + str(round(self.fitness, precision)) + ',' + str(self.objective) + ',' + str(round(self.evalTime, precision)) + ',' + str(self) + ',' + self.solution
	
	def init(self):
		# allocate memory for the individual
		for i in range(self.chromosomeLength):
			self.chromosome.append(0)

	def setSeed(self, seed):
		random.seed(seed)
	
	def randomize(self):
		self.chromosome = self.eval.getRandomString()
		self.evaluate()

	def evaluate(self):
		# run the evaluation using the evalution obj
		result = self.eval.evaluate(self.chromosome)

		# assign the results to the individual
		self.fitness = result[0]
		self.objective = result[1]
		self.evalTime = result[2]
		self.solution = result[3]
		return result

	def swap(self, p1, p2):
		temp = self.chromosome[p1]
		self.chromosome[p1] = self.chromosome[p2]
		self.chromosome[p2] = temp

	def invert(self, p1, p2):
		minp = min(p1, p2)
		maxp = max(p1, p2)
		for i in range(minp, maxp, 1):
			p1 = minp + i
			p2 = maxp - i
			if p1 >= p2:
				break
			temp = self.chromosome[p1]
			self.chromosome[p1] = self.chromosome[p2]
			self.chromosome[p2] = temp

	def mutate(self):
		for i in range(self.chromosomeLength):
			if random.random() < self.options.pMut:
				self.swap(i, random.randint(0, self.chromosomeLength - 1))

	def copy(self, ind):
		self.fitness = ind.fitness
		self.objective = ind.objective
		self.evalTime = ind.evalTime
		self.chromosomeLength = ind.chromosomeLength # this should not change!
		self.objective = ind.objective
		for i in range(self.chromosomeLength):
			self.chromosome[i] = ind.chromosome[i]
