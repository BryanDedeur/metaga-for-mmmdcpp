import individual
import random
import statistics
from router import Router
import tour
import copy
import math
from timeit import default_timer as timer


class Evaluator:
	def __init__(self, gph, numTours, router):
		# variables
		self.version = 3.0
		self.graph = gph
		self.numTours = numTours
		self.router = router
		self.depotNode = 0
		self.routerStats = statistics.Statistics()
		self.timeStats = statistics.Statistics()
		self.count = 0

		self.bestRouter = None
		self.bestObjective = None
		self.bestEncoding = []
		self.bestDecoding = []
		self.bestEvalCount = 0

		self.seed = 0000

		# encoding
		self.geneLength = 0
		self.chromeLength = 0

		self.minAllele = 0
		self.maxAllele = 3

		self.heuristics = []
	
	def reset(self):
		self.routerStats.clear()
		self.timeStats.clear()
		self.count = 0
		self.bestRouter = None
		self.bestObjective = None
		self.bestEncoding = []
		self.bestDecoding = []
		self.bestEvalCount = 0

	def to_string(self, delimiter = ",", ending = '\n'):
		data = [
			self.GetProblemName(),
			self.graph.size_e(),
			self.numTours,
			self.seed,
			self.bestObjective,
			round(self.timeStats.sum, 3),
			self.bestEvalCount
			]
		for k in range(len(self.router.tours)):
			data.append(self.bestRouter.tours[k].cost)
		formatted = ''
		for i in range(len(data)):
			formatted += str(data[i])
			if i < len(data) - 1:
				formatted += delimiter
			else:
				formatted += ending
		return formatted

	def save(self, path, save_best_routes = False):
		f = open(path, "a")
		f.write(self.to_string())
		f.close()
		if save_best_routes:
			self.bestRouter.save()

	def GetProblemName(self):
		return self.graph.name

	def setSeed(self, seed):
		random.seed(seed)
		self.router.setSeed(seed)
		self.seed = seed
	
	def getRandomString(self):
		# make array using base 0 indicies not size of actual data
		temp = []
		for i in range(self.chromeLength):
			temp.append(random.randint(0, 1))
		return temp

	def decode(self, encoding):
		decoding = []
		for i in range(0, len(encoding), self.geneLength):
			decimal = 0
			for j in range(self.geneLength):
				decimal = decimal * 2 + encoding[i + j]
			decoding.append(decimal)
		return decoding

	def storeIfBest(self, router, encoding, decoding, count):
		# keep track of the shortest tour
		longestTourLength = router.getLengthOfLongestTour()
		if self.bestRouter == None:
			self.bestRouter = Router(self.graph, len(router.tours))
			self.bestRouter.copy(router)
			self.bestObjective = longestTourLength
			self.bestEncoding = []
			for b in encoding:
				self.bestEncoding.append(b)
			self.bestDecoding = []
			for d in decoding:
				self.bestDecoding.append(d)
			self.bestEvalCount = count
			return True
		elif longestTourLength < self.bestObjective:
			self.bestRouter.copy(router)
			self.bestObjective = longestTourLength
			self.bestEncoding = []
			for b in encoding:
				self.bestEncoding.append(b)
			self.bestDecoding = []
			for d in decoding:
				self.bestDecoding.append(d)
			self.bestEvalCount = count
			return True
		return False

	def evaluate(self, encodedData):
		# start a timer
		self.count += 1
		start = timer()

		decoding = self.decode(encodedData)

		self.router.clear()
		# add first vertex to tour
		for tour in self.router.tours:
			tour.add_vertex(tour.depot)

		# convert the heuristics to tours
		for h in decoding:
			self.heuristics[h](h)

		# return all tours to their depots
		for tour in self.router.tours:
			tour.add_vertex(tour.depot)

		# end time track stats
		time_elapsed = timer() - start
		self.timeStats.addValue(time_elapsed)
		self.storeIfBest(self.router, encodedData, decoding, self.count)

		return 1/self.router.getLengthOfLongestTour(), self.router.getLengthOfLongestTour(), time_elapsed, self.router.data_str()

