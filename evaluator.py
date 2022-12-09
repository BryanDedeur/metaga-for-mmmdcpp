import individual
import random
import statistics
import tour
import copy
import math
from timeit import default_timer as timer

from router import Router

class Evaluator:
	def __init__(self, gph, numTours):
		# variables
		self.version = 3.0
		self.graph = gph
		self.numTours = numTours
		self.router = Router(self.graph, numTours)
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
		self.geneLength = round(math.sqrt(len(self.router.heuristics))) # num bits (1 bits = 2 heuristics) (2 bits = 4 heursitics) (3 bits = 8 heuristics)
		self.chromeLength = self.graph.SizeE() * self.geneLength

		self.minAllele = 0
		self.maxAllele = 3

		self.chromosome_counter = [] # keeps track of heuristic frequency
		
		for i in range(self.graph.SizeE()):
			self.chromosome_counter.append({0: 0, 1: 0, 2: 0, 3: 0, -1: 0})

	def count_heuristic_frequency(self, decoding):
		# decoding = heuristic, numEquidistant, totalNumber
		# take count of occurances
		for i in range(len(self.chromosome_counter)):
			if decoding[i][1] == 1:
				self.chromosome_counter[i][-1] += 1
			else:
				self.chromosome_counter[i][decoding[i][0]] += 1 
		
	def reset_heuristic_frequency(self):
		for i in range(len(self.chromosome_counter)):
			for key, value in self.chromosome_counter[i].items():
				self.chromosome_counter[i][key] = 0

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
			self.graph.SizeE(),
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

	def save(self, path):
		f = open(path, "a")
		f.write(self.to_string())
		f.close()
		self.bestRouter.save("test")

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
	
	def binToDec(self, binary):
		decimal = 0
		count = 0
		for i in binary:
			if i == 1:
				decimal += pow(2, count)
			count += 1
		return decimal

	def decode(self, encoding):
		decoding = []
		for i in range(0, len(encoding), self.geneLength):
			decoding.append(self.binToDec(encoding[i: i + self.geneLength]))
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

	def evaluate(self, encodedData, stringId = -1):
		# start a timer
		self.count += 1
		start = timer()

		decoding = self.decode(encodedData)

		self.router.clear()
		for k_i in range(self.numTours):
			k_depot = self.graph.SizeV() - (k_i - (math.floor(k_i/4)*4)) - 1
			self.router.addVertexToTour(k_depot, self.router.tours[k_i])

		number_of_edge_options = self.router.processHeuristicSequence(decoding)

		for k_i in range(self.numTours):
			k_depot = self.graph.SizeV() - (k_i - (math.floor(k_i/4)*4)) - 1
			self.router.addVertexToTour(k_depot, self.router.tours[k_i])

		# statistics
		#self.routerStats.addValue(self.router.getLengthOfLongestTour())
		#print('Average eval time: ' + str(self.timeStats.mean()))
			#print(self.router.getLengthOfLongestTour())

		endTime = timer() - start
		self.timeStats.addValue(endTime)
		isBest = self.storeIfBest(self.router, encodedData, decoding, self.count)
		# if (isBest):
		# 	print("NICE")
		#self.count_heuristic_frequency(decoding_with_unused_heuristics)

		return 1/self.router.getLengthOfLongestTour(), self.router.getLengthOfLongestTour(), endTime, stringId, number_of_edge_options, decoding

