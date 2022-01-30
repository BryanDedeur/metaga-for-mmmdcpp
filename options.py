from enum import Enum

class SelectionType(Enum):
	Roulette = 0

class CrossoverType(Enum):
	OnePoint = 0
	TwoPoint = 1
	Uniform = 2
	PMX = 3

class MutationType(Enum):
	Swap = 0
	Invert = 1

class Options:
	def __init__(self):
		self.populationSize = 100
		self.maxGen = int(1.5 * self.populationSize)

		self.selectionType = SelectionType.Roulette
		self.linearFitnessScaling = True
		self.tournament = False
		self.niching = False
		self.crossType = CrossoverType.TwoPoint
		self.pCross = 0.99
		self.mutType = MutationType.Invert
		self.pMut = 0.1

		self.chcLambda = 2

		self.resultsFile = 'results.txt'
		self.resultsDir = '/results/'

	def to_string(self, delimiter = ',', ending = '\n'):
		data = [
			self.populationSize,
			self.maxGen,
			self.selectionType,
			self.linearFitnessScaling,
			self.tournament,
			self.niching,
			self.crossType,
			self.pCross,
			self.mutType,
			self.pMut,
			]
		formatted = ''
		for i in range(len(data)):
			formatted += str(data[i])
			if i < len(data) - 1:
				formatted += delimiter
			else:
				formatted += ending
		return formatted


