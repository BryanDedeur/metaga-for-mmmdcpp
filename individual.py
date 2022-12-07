import random
import evaluator

class Individual:
	def __init__(self, population):
		self.population = population
		self.options = population.options
		self.eval = population.eval

		self.chromosome = []
		self.chromosomeLength = self.eval.chromeLength

		self.fitness = 0
		self.objective = 0
		self.evalTime = 0

		self.result_heursitics_used = []

		self.scaledFitness = 0
	
	# allocates memory for the individual
	def init(self):
		for i in range(self.chromosomeLength):
			self.chromosome.append(0)

	def setSeed(self, seed):
		random.seed(seed)
	
	def randomize(self):
		self.chromosome = self.eval.getRandomString()
		self.evaluate()

	def evaluate(self, evaluator=None, id=-1):
		# if we are parallelizing the individual might need a specific evaluator on a seperate core
		result = None
		if evaluator == None:
			result = self.eval.evaluate(self.chromosome)
		else:
			result = evaluator.evaluate(self.chromosome, id)

		# assign the results to the individual
		self.fitness = result[0]
		self.objective = result[1]
		self.evalTime = result[2]
		self.result_heursitics_used = result[4]
		
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
