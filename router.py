import tour
import random

from graph import Graph
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.lines import Line2D


class Router:
	def __init__(self, gph, numTours):
		self.graph = gph
		self.tours = []
		self.nearestEdgesSetSize = self.graph.SizeE()
		self.seed = 0

		for i in range(numTours):
			self.tours.append(tour.Tour(self.graph))
			self.tours[i].k = numTours

		self.colors = ['red', 'blue', 'green', 'orange', 'purple', 'maroon', 'deepskyblue', 'lime', 'gold', 'hotpink']

		self.visitedEdges = []
		self.unvisitedEdges = []

		# self.heuristics = [
		# 	self.findLowestCostUnvisitedEdge, 
		# 	self.findHighestCostUnvisitedEdge, 
		# 	self.findRandomUnvisitedEdge, 
		# 	self.findRandomUnvisitedEdgeConnectedToVisitedVertices,
		# 	self.findLowestCostNearestUnvisitedEdge,
		# 	self.findHighestCostNearestUnvisitedEdge,
		# 	self.findRandomCostNearestUnvisitedEdge,
		# 	self.findLowestCostNearestUnvisitedEdge
		# 	]
		# self.heuristicEdgeCandidates = 'Set of Equi Distant'
		# self.heuristicEdgeSelection = 'Min, Mid, Max, Rand'

		self.heuristics = [
			# same distance unvisited edges
			self.findLowestCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges,
			self.findMidCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges,
			self.findRandomCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges,
			self.findHighestCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges,
			# until set size of univisted egdes
			# self.findLowestCostNearestUnvisitedEdge,
			# self.findMidCostNearestUnvisitedEdge,
			# self.findRandomCostNearestUnvisitedEdge,
			# self.findHighestCostNearestUnvisitedEdge
			# edges of degree
			#self.findEdgeConnectedToOddDegreeVertexWithinNearestUnivistedEdges
			#self.findEdgeConnectedToEvenDegreeVertexWithinNearestUnivistedEdges
			]
		
		self.heuristicSelectionCounter = []
		for h in range(len(self.heuristics)):
			self.heuristicSelectionCounter.append(0)
	
	def size(self):
		return len(self.tours)

	def setSeed(self, seed):
		self.seed = seed
		random.seed(seed)
		for k in range(len(self.tours)):
			self.tours[k].seed = seed

	def View(self):
		i = 0
		# fig, ax = plt.subplots()
		# sizex = 1
		# sizey = 1
		for tour in self.tours:
			axe = tour.View(i, self.colors[i])
			# fig.axes.append(axe)
			# fig.add_axes(axe)

			i += 1
		# plt.show()
		fig, ax = plt.subplots(1, figsize=(4, 4))
		ax.title.set_text('graph ' + self.graph.name.lower())
		self.ViewOverlap(ax)
		plt.savefig(fname='img/' + self.graph.name +'-k'+str(len(self.tours))+'-'+str(self.seed) +'-overlap')
		plt.close()

	def colorFader(self, c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
		c1=np.array(mpl.colors.to_rgb(c1))
		c2=np.array(mpl.colors.to_rgb(c2))
		return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

	def ViewOverlap(self, ax):
		edgeVisits = []
		for e in range(self.graph.SizeE()):
			edgeVisits.append(0)
		for tour in self.tours:
			for e in tour.edgeSequence:
				edgeVisits[e] += 1

		x = []
		y = []

		minCount = min(edgeVisits)
		maxCount = max(edgeVisits)
		minColor = 'dodgerblue'
		maxColor = 'red'
		for e in range(self.graph.SizeE()):
			vpair = self.graph.GetEdgeVertices(e)
			x = (self.graph.vertices[vpair[0]][0], self.graph.vertices[vpair[1]][0])
			y = (self.graph.vertices[vpair[0]][1], self.graph.vertices[vpair[1]][1])
			ax.plot(x, y, color=self.colorFader(minColor,maxColor,(edgeVisits[e] - 1)/(maxCount - minCount)), linewidth=2 * edgeVisits[e])
		legend_elements = [
			Line2D([0], [0], color=minColor, linewidth=2 * minCount, label=str(minCount) + " visits"),
			Line2D([0], [0], color=maxColor, linewidth=2 * maxCount, label=str(maxCount) + " visits")]
		#ax.legend(handles=legend_elements, loc='upper right')

	def to_string(self, delimiter = ',', ending = '\n'):
		data = [
			len(self.tours), 
			self.getSumTourLengths(),
			self.getLengthOfLongestTour()
			]
		formatted = ''
		for i in range(len(data)):
			formatted += str(data[i])
			if i < len(data) - 1:
				formatted += delimiter
			else:
				formatted += ending
		return formatted

	def save(self, path):
		# f = open(path, "a")
		# f.write(self.to_string())
		# f.close()
		self.View()

	def copy(self, other):
		self.graph = other.graph
		self.tours = []
		for t in range(len(other.tours)):
			self.tours.append(tour.Tour(self.graph))
			self.tours[t].seed = other.seed
			self.tours[t].k = len(other.tours)
		for i in range(len(self.tours)):
			for v in other.tours[i].vertexSequence:
				self.tours[i].AddVertex(v)
		self.unvisitedEdges = []
		for e in other.unvisitedEdges:
			self.unvisitedEdges.append(e)
		for e in other.visitedEdges:
			self.visitedEdges.append(e)
		self.seed = other.seed
		
	def getSumTourLengths(self):
		sum = 0
		for i in self.tours:
			sum += i.cost
		return sum

	def clear(self):
		for i in range(len(self.tours)):
			self.tours[i].clear()
		self.unvisitedEdges.clear()
		self.visitedEdges.clear()
		for i in range(self.graph.SizeE()):
			self.unvisitedEdges.append(i)

	def processHeuristicSequence(self, sequence):
		temp = []
		for h in sequence:
			h_temp = h
			# increase the counter
			self.heuristicSelectionCounter[h] += 1
			# find edge using heuristic
			shortestTour = self.getShortestTour()
			e, equidistantEdges, totalEdges = self.heuristics[h](shortestTour, self.nearestEdgesSetSize)
			if equidistantEdges <= 1:
				h_temp = -1
			self.addEdgeToTour(e, shortestTour)
			# update sequence if no heuristic is used
			temp.append(equidistantEdges)
		return temp

	def getUnvisitedEdges(self):
		return self.unvisitedEdges
	
	def getLongestTour(self):
		foundTour = None
		tempLength = 0
		for tour in self.tours:
			if tour.cost > tempLength:
				foundTour = tour
				tempLength = tour.cost
		return foundTour

	def getShortestTour(self):
		foundTour = None
		tempLength = float('inf')
		for tour in self.tours:
			if tour.cost < tempLength:
				foundTour = tour
				tempLength = tour.cost
		return foundTour

	def getLengthOfLongestTour(self):
		return self.getLongestTour().cost

	def getSetOfNearestEdges(self, vertex, maxSetSize = -1, sort = True):
		allShortestTourEdgePairs = self.getShortestToursToAllUnvisitedEdgesFromVertex(vertex)
		if len(allShortestTourEdgePairs) == 0:
			return [], len(allShortestTourEdgePairs)
		setOfEdges = []
		distanceToNearestEdges = allShortestTourEdgePairs[0][0].cost
		for tourEdgePair in allShortestTourEdgePairs:
			if maxSetSize != -1:
				# append until max set size
				if len(setOfEdges) < maxSetSize:
					setOfEdges.append(tourEdgePair[1])
				else:
					break
			else:
				# continue appending same distance edges
				if tourEdgePair[0].cost == distanceToNearestEdges:
					setOfEdges.append(tourEdgePair[1])
				else:
					break 
		def getLengthOfEdge(edgeId):
			return self.graph.GetEdgeCost(edgeId), len(allShortestTourEdgePairs)
		if sort:
			setOfEdges.sort(key=getLengthOfEdge)
		# for e in setOfEdges:
		# 	print(self.graph.GetEdgeCost(e))
		return setOfEdges, len(allShortestTourEdgePairs)

	# ============================================== HEURISTICS FOR EDGE FINDING ================================================================= #

	def findLowestCostUnvisitedEdge(self):
		lowestEdge = -1
		lowestEdgeValue = float('inf')
		for e in self.unvisitedEdges:
			if self.graph.GetEdgeCost(e) < lowestEdgeValue:
				lowestEdge = e
				lowestEdgeValue = self.graph.GetEdgeCost(e)
		return lowestEdge
	
	def findHighestCostUnvisitedEdge(self):
		lowestEdge = -1
		lowestEdgeValue = 0
		for e in self.getUnvisitedEdges():
			if self.graph.GetEdgeCost(e) > lowestEdgeValue:
				lowestEdge = e
				lowestEdgeValue = self.graph.GetEdgeCost(e)
		return lowestEdge
	
	# def findRandomUnvisitedEdge(self):
	# 	unvisited = self.getUnvisitedEdges()
	# 	if len(unvisited) > 0:
	# 		return unvisited[random.randint(0, len(unvisited) - 1)]
	# 	return -1
	
	# def findRandomUnvisitedEdgeConnectedToVisitedVertices(self):
	# 	unvisited = self.getUnvisitedEdges()
	# 	if len(unvisited) > 0:
	# 		return unvisited[random.randint(0, len(unvisited) - 1)]
	# 	return -1

	def findLowestCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges(self, tourOfInterest, setSize):
		# setOfSortedLengthEdges = []
		# if self.graph.GetEdgeDegreeAtVertex(tourOfInterest.vertexSequence[-1]) % 2 != 0:
		# 	# TODO maybe consider also if the number of visited edges at vertex = 0
		# 	setOfSortedLengthEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1], setSize)
		# else:
		setOfSortedLengthEdges, totalUnvisitedEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1])
		
		if len(setOfSortedLengthEdges) == 0:
			return -1, 0, totalUnvisitedEdges
		return setOfSortedLengthEdges[0], len(setOfSortedLengthEdges), totalUnvisitedEdges

	def findMidCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges(self, tourOfInterest, setSize):
		# setOfSortedLengthEdges = []
		# if self.graph.GetEdgeDegreeAtVertex(tourOfInterest.vertexSequence[-1]) % 2 != 0:
		# 	# TODO maybe consider also if the number of visited edges at vertex = 0
		# 	setOfSortedLengthEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1], setSize)
		# else:
		setOfSortedLengthEdges, totalUnvisitedEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1])
		if len(setOfSortedLengthEdges) == 0:
			return -1, 0, totalUnvisitedEdges
		return setOfSortedLengthEdges[int((len(setOfSortedLengthEdges) - 1) / 2)], len(setOfSortedLengthEdges), totalUnvisitedEdges

	def findRandomCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges(self, tourOfInterest, setSize):
		# setOfSortedLengthEdges = []
		# if self.graph.GetEdgeDegreeAtVertex(tourOfInterest.vertexSequence[-1]) % 2 != 0:
		# 	# TODO maybe consider also if the number of visited edges at vertex = 0
		# 	setOfSortedLengthEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1], setSize)
		# else:
		setOfSortedLengthEdges, totalUnvisitedEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1])
		if len(setOfSortedLengthEdges) == 0:
			return -1, 0, totalUnvisitedEdges
		return setOfSortedLengthEdges[random.randint(0, len(setOfSortedLengthEdges) - 1)], len(setOfSortedLengthEdges), totalUnvisitedEdges

	def findHighestCostUnvisitedEdgeFromSetOfNearestSameDistanceEdges(self, tourOfInterest, setSize):
		# setOfSortedLengthEdges = []
		# if self.graph.GetEdgeDegreeAtVertex(tourOfInterest.vertexSequence[-1]) % 2 != 0:
		# 	# TODO maybe consider also if the number of visited edges at vertex = 0
		# 	setOfSortedLengthEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1], setSize)
		# else:
		setOfSortedLengthEdges, totalUnvisitedEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1])
		if len(setOfSortedLengthEdges) == 0:
			return -1, 0, totalUnvisitedEdges
		return setOfSortedLengthEdges[len(setOfSortedLengthEdges) - 1], len(setOfSortedLengthEdges), totalUnvisitedEdges

	def findLowestCostNearestUnvisitedEdge(self, tourOfInterest, setSize):
		setOfSortedLengthEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1], setSize)
		if len(setOfSortedLengthEdges) == 0:
			return -1
		return setOfSortedLengthEdges[0]

	def findMidCostNearestUnvisitedEdge(self, tourOfInterest, setSize):
		setOfSortedLengthEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1], setSize)
		if len(setOfSortedLengthEdges) == 0:
			return -1
		return setOfSortedLengthEdges[int((len(setOfSortedLengthEdges) - 1) / 2)]

	def findRandomCostNearestUnvisitedEdge(self, tourOfInterest, setSize):
		setOfSortedLengthEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1], setSize)
		if len(setOfSortedLengthEdges) == 0:
			return -1
		return setOfSortedLengthEdges[random.randint(0, len(setOfSortedLengthEdges) - 1)]

	def findHighestCostNearestUnvisitedEdge(self, tourOfInterest, setSize):
		setOfSortedLengthEdges = self.getSetOfNearestEdges(tourOfInterest.vertexSequence[-1], setSize)
		if len(setOfSortedLengthEdges) == 0:
			return -1
		return setOfSortedLengthEdges[len(setOfSortedLengthEdges) - 1]

	# finds the first edge with the arriving vertex (using dijkstras) being odd degree
	def findEdgeConnectedToOddDegreeVertexWithinNearestUnivistedEdges(self, tourOfInterest, setSize):
		unvisitedTourEdgePairs = self.getShortestToursToAllUnvisitedEdgesFromVertex(tourOfInterest.vertexSequence[-1])
		if len(unvisitedTourEdgePairs) == 0:
			return -1
		for tourEdgePair in unvisitedTourEdgePairs:
			if self.graph.GetEdgeDegreeAtVertex(tourEdgePair[0].vertexSequence[-1]) % 2 != 0:
				return tourEdgePair[1]
		return unvisitedTourEdgePairs[0][1]

	# finds the first edge with the arriving vertex (using dijkstras) being odd degree
	def findEdgeConnectedToEvenDegreeVertexWithinNearestUnivistedEdges(self, tourOfInterest, setSize):
		unvisitedTourEdgePairs = self.getShortestToursToAllUnvisitedEdgesFromVertex(tourOfInterest.vertexSequence[-1])
		if len(unvisitedTourEdgePairs) == 0:
			return -1
		for tourEdgePair in unvisitedTourEdgePairs:
			if self.graph.GetEdgeDegreeAtVertex(tourEdgePair[0].vertexSequence[-1]) % 2 != 0:
				return tourEdgePair[1]
		return unvisitedTourEdgePairs[0][1]

	# def findRandomCostNearestUnvisitedEdge(self):
	# 	unvisitedEdgesSortedByDistance = self.getShortestToursToAllUnvisitedEdgesFromVertex(self.tours[self.shortestTourId].vertexSequence[-1])
	# 	setOfEdges = []
	# 	shortestTourLen = float('inf')
	# 	for tourEdgePair in unvisitedEdgesSortedByDistance:
	# 		if tourEdgePair[0].cost <= shortestTourLen:
	# 			shortestTourLen = tourEdgePair[0].cost
	# 			setOfEdges.append(tourEdgePair[1])
	# 		else:
	# 			break
	# 	if len(setOfEdges) == 0:
	# 		return -1
	# 	return setOfEdges[random.randint(0, len(setOfEdges) - 1)]

	# ============================================== HEURISTICS FOR EDGE FINDING ================================================================= #

	def addVertexToTours(self, vertexId):
		for tour in self.tours:
			tour.AddVertex(vertexId)

	def addVertexToTour(self, vertexId, tour):
		tour.AddVertex(vertexId)

	def addEdgeToTour(self, edgeId, tour):
		if edgeId != -1:
			numEdgesInTourBeforeAddedEdges = len(tour.edgeSequence)
			tour.AddEdge(edgeId)
			
			# mark all edges along shortest path as visted
			for e in range(numEdgesInTourBeforeAddedEdges, len(tour.edgeSequence)):
				edge = tour.edgeSequence[e]
				if edge in self.unvisitedEdges:
					self.unvisitedEdges.remove(edge)
					self.visitedEdges.append(edge)

	def getShortestToursToAllUnvisitedEdgesFromVertex(self, vertex, sortTours = True):
		tempToursToEdges = []
		for e in self.getUnvisitedEdges():
			tempToursToEdges.append((self.graph.GetShortestTourBetweenVertexAndEdge(vertex, e), e))
		def getTourLengthFromPair(tourEdgePair):
			return tourEdgePair[0].cost
		if sortTours:
			tempToursToEdges.sort(key=getTourLengthFromPair)
		return tempToursToEdges

	def getShortestToursToEdgesFromVertex(self, edges, vertex, sortTours = True):
		tempToursToEdges = []
		for e in edges:
			tempToursToEdges.append((self.graph.GetShortestTourBetweenVertexAndEdge(vertex, e), e))
		def getTourLengthFromPair(tourEdgePair):
			return tourEdgePair[0].cost
		if sortTours:
			tempToursToEdges.sort(key=getTourLengthFromPair)
		return tempToursToEdges

	def buildToursWithSimpleHeuristic(self):
		# builds tours by always assigning nearest unvisited edges to the shortest tour
		self.addVertexToTours(0)

		while (len(self.getUnvisitedEdges()) > 0):
			toursToEdges = self.getShortestToursToAllUnvisitedEdgesFromVertex(self.getShortestTour().vertexSequence[-1])
			self.addEdgeToTour(toursToEdges[0][1], self.getShortestTour())

		self.addVertexToTours(0)


