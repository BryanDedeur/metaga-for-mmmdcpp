import os
import json
import matplotlib.pyplot as plt
import numpy as np
import os

from posixpath import split
from typing import Sized
from tour import Tour

class Graph:
    def __init__(self, filepath = ''):
        self.name = ''
        self.fileName = ''
        self.adjacencyMatrix = [] # [][] of edge costs
        self.edgeMatrix = [] # [][] of adjacency matrix with edge ID's instead of costs
        self.edgeIds = [] # (v1, v2)
        self.vertices = [] # (x coordiante, y coordinate)
        self.connectedEdges = [] # [vertex id] = [edges]
        self.cachedDijkstras = [] #[][] of tours
        self.filepath = filepath

        if (filepath):
            split_tup = os.path.splitext(filepath)
            nameWithoutExtension = split_tup[0]
            self.fileName = nameWithoutExtension.split('/')[len(nameWithoutExtension.split('/')) - 1]
            splitName = self.fileName.lower().split('-')
            for st in splitName:
                self.name += st + ' '
            directory = nameWithoutExtension.split(self.name)[0]
            extension = split_tup[1]
            if extension == '.csv':
                self.LoadCSVFile(filepath)
            elif extension == '.json':
                self.LoadJSONFile(filepath)
            elif extension == '.dat':
                self.LoadDATFile(filepath)
            
            if len(self.vertices) < len(self.adjacencyMatrix):
                # check for obj file
                objpath = directory + '.obj'
                if (os.path.exists(objpath)):
                    self.loadVertices(objpath)
                else:
                    self.createVertexPositions()

    def createVertexPositions(self):
        theta_distribution = np.linspace(0, 2 * np.pi, self.SizeV() + 1)
        radius = 1
        a = radius * np.cos(theta_distribution)
        b = radius * np.sin(theta_distribution)
        for v in range(self.SizeV()):
            self.vertices.append((a[v], b[v]))
        return

    def loadVertices(self, path):
        print("Loading coordinates: " + path)
        file = open(path, 'r')
        lines = file.readlines()
        file.close()
        for v in range(len(lines)):
            cols = lines[v].split(' ')
            if len(cols) == 4:
                self.vertices.append((float(cols[1]), float(cols[2])))
        return

    def plot(self, ax, annotate_vertices, annotate_edges):
        # plot the graph
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        ax.axes.xaxis.set_ticklabels([])
        ax.axes.yaxis.set_ticklabels([])
        # plot the edges
        for vPair in self.edgeIds:
            v1 = vPair[0]
            v2 = vPair[1]
            x = (self.vertices[v1][0], self.vertices[v2][0])
            y = (self.vertices[v1][1], self.vertices[v2][1])
            ax.plot(x, y, color="gray")
            if annotate_edges:
                xy = (x[1] + (x[0] - x[1])/2, y[1] + (y[0] - y[1])/2)
                ax.annotate(str(self.edgeMatrix[v1][v2]), xy ,ha='center',va='center', color = "white",size = 6,
                            bbox=dict(boxstyle="circle,pad=0.2", fc="gray", ec="b", lw=0))
        # plot the vertices
        x = []
        y = []
        for v in range(len(self.vertices)):
            x.append(self.vertices[v][0])
            y.append(self.vertices[v][1])
            if annotate_vertices:
                xy = (self.vertices[v][0], self.vertices[v][1])
                ax.annotate(str(v), xy ,ha='center',va='center', color = "white",size = 6,
                            bbox=dict(boxstyle="circle,pad=0.2", fc="teal", ec="b", lw=0))
    
    def View(self, blocking):
        fig, ax = plt.subplots(1, figsize=(4, 4))
        ax.title.set_text('graph ' + self.name)
        self.plot(ax, True, True)
        plt.show(block = blocking)

    def LoadCSVFile(self, file):
        print("Loading graph: " + file)
        file = open(file, 'r')
        lines = file.readlines()
        file.close()
        count = 0
        for r in range(len(lines)):
            cols = lines[r].split(',')
            for c in range(r, len(cols)):
                edgeCost = float(cols[c])
                if edgeCost > 0:
                    self.AddEdge(r, c, edgeCost)
                    count += 1
        return

    def LoadDATFile(self, file):
        print("Loading graph: " + file)
        file = open(file, 'r')
        lines = file.readlines()
        file.close()
        for line in lines:
            bad_chars = ['(', ',', ')']
            for i in bad_chars:
                line = line.replace(i, '')
            numbers = []
            for t in line.split():
                try:
                    numbers.append(float(t))
                except ValueError:
                    pass
            if len(numbers) >= 3:
                self.AddEdge(int(numbers[0] - 1), int(numbers[1] - 1), numbers[2])
        return

    def LoadJSONFile(self, file):
        print("Loading graph: " + file)
        file = open(file, 'r')
        data = json.load(file)
        file.close()
        #for (int e = 0; e < js["edges"].size(); ++e) {
        edgesKey = 'edges'
        vertexKey = 'vIDs'
        for e in range(len(data[edgesKey])):
            v1 = data[edgesKey][e][vertexKey][0]
            v2 = data[edgesKey][e][vertexKey][1]
            cost = float(data[edgesKey][e]['length'])
            self.AddEdge(v1, v2, cost)

        # load vertice positions
        for v in range(len(data['vertices'])):
            coord = data['vertices'][v]['v2Pos']
            self.vertices.append((coord[0], 10 - coord[1]))
        return
    
    def Clear(self):
        self.adjacencyMatrix.clear()
        self.edgeMatrix.clear()
        self.edgeIds.clear()
        self.cachedDijkstras.clear()
        self.connectedEdges.clear()

    def SizeV(self):
        return len(self.adjacencyMatrix)

    def SizeE(self):
        return len(self.edgeIds)
    
    def SumE(self):
        sum = 0
        for e in self.edgeIds:
            sum += self.GetEdgeCost(e)
        return sum

    def to_string(self, delimiter = ',', ending = '\n'):
        data = [
            self.name(),
            self.SizeE(),
            self.SizeV(),
            self.SumE()
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
        f = open(path, "a")
        f.write(self.to_string())
        f.close()

    # Fixes the adjacency matrix dimenions if not the right size for the vertex id.
    def FixDimensions(self, newLim):
        # Zero base indexing means we need to increase the counts to 1+ newLim
        newLim += 1
        # Extend the size of the matrix to match the new limit
        i = self.SizeV() - 1
        while (self.SizeV() < newLim):
            i += 1
            self.adjacencyMatrix.append([])
            self.cachedDijkstras.append([])
            self.edgeMatrix.append([])
        # Fix the cols
        for i in range(newLim):
            while (len(self.adjacencyMatrix[i]) < newLim):
                self.adjacencyMatrix[i].append(0)
                self.cachedDijkstras[i].append(Tour(self))
                self.edgeMatrix[i].append(-1)


    def IsValidEdge(self, v1,  v2):
        if (self.edgeMatrix[v1][v2] > -1):
            return True
        # Invalid edge
        #pr("Trying to access edge between vertices (" + v1.ToString() + " " + v2.ToString() + ") which is not valid.")
        return False

    def GetEdgeVertices(self, id):
        return self.edgeIds[id]
        # for r in range(len(self.edgeMatrix)):
        #     for c in range(len(self.edgeMatrix)):        
        #         if (self.edgeMatrix[r][c] == id):
        #             return (r, c)
        # # This is dangerous but nescessary to flag issues
        # print("Edge id:" + str(id) + " does not exist, but trying to access it.")
        # return (-1,-1)

    def GetEdge(self, v1,  v2):
        if (not self.IsValidEdge(v1, v2)):
            return -1
        return self.edgeMatrix[v1][v2]

    def GetEdgeCostFromVertices(self, v1,  v2):
        return self.adjacencyMatrix[v1][v2]
    
    def GetEdgeCost(self, id):
        vertices = self.GetEdgeVertices(id)
        return self.GetEdgeCostFromVertices(vertices[0], vertices[1])

    def GetOppositeVertexOnEdge(self, vertex,  edge):
        vertices = self.GetEdgeVertices(edge)
        if (vertices[0] == vertex):
            return vertices[1]
        return vertices[0]
    
    def GetShortestTourBetweenVertices(self, startVertex,  endVertex):
        # pr(startVertex.ToString() + endVertex.ToString())
        tour = self.cachedDijkstras[startVertex][endVertex]
        if (tour == None):
            tour = self.cachedDijkstras[endVertex][startVertex]
        return tour
    
    def GetShortestTourBetweenVertexAndEdge(self, vertex,  edge):
        evs = self.GetEdgeVertices(edge)
        tour = self.GetShortestTourBetweenVertices(vertex, evs[0])
        bestTour = tour
        if (tour.cost < bestTour.cost):
            bestTour = tour
        tour = self.GetShortestTourBetweenVertices(vertex, evs[1])
        if (tour.cost < bestTour.cost):
            bestTour = tour
        return bestTour

    def GetShortestTourBetweenEdges(self, edge1,  edge2):
        e1vs = self.GetEdgeVertices(edge1)
        tour1 = self.GetShortestTourBetweenVertexAndEdge(e1vs[0], edge2)
        tour2 = self.GetShortestTourBetweenVertexAndEdge(e1vs[1], edge2)
        if (tour1.cost < tour2.cost):
            return tour1
        return tour2
    
    # returns the vertex inbetween two edges
    def GetEdgesConnectingVertex(self, edge1,  edge2):
        vertices1 = self.GetEdgeVertices(edge1)
        vertices2 = self.GetEdgeVertices(edge2)
        if (vertices1[0] == vertices2[0]):
            return vertices1[0]
        elif (vertices1[0] == vertices2[1]):
            return vertices1[0]
        elif (vertices1[1] == vertices2[0]):
            return vertices1[1]
        elif (vertices1[1] == vertices2[1]):
            return vertices1[1]
        return -1

    def GetSetOfEdgesConnectedToVertex(self, vertexId):
        return self.connectedEdges[vertexId]

    def GetEdgeDegreeAtVertex(self, vertexId):
        return len(self.GetSetOfEdgesConnectedToVertex(vertexId))

    def AddVertex(self, vId):
        # Make sure the adjacency matrix is the right size
        self.FixDimensions(vId)
        # all we need to do is make sure the adjacency matrix is the right size

    # Add a new edge to the adjacency matrix
    def AddEdge(self, v1,  v2,  cost):
        id = self.SizeE()
        # Add vertices regarless if they exist because add vertex will resolve that
        self.AddVertex(v1)
        self.AddVertex(v2)
        # make sure edge does not already exist
        if (self.edgeMatrix[v1][v2] == -1):
            self.edgeIds.append((v1, v2))
            self.adjacencyMatrix[v1][v2] = cost
            self.adjacencyMatrix[v2][v1] = cost
            self.edgeMatrix[v1][v2] = id
            self.edgeMatrix[v2][v1] = id
        
    def minDistance(self, dist, spSet):
        best = (-1, float('inf'))
        for v in range(self.SizeV()):
            if (not spSet[v] and dist[v] <= best[1]):
                best = (v, dist[v])
        if (best[0] == -1):
            print("No better min distance found, so returning an invalid vertex.")
        return best[0]

    def Dijkstras(self, src):
        # initialization
        dist = []
        spSet = [] 
        for i in range(self.SizeV()):
            dist.append(float('inf'))
            spSet.append(False)
            self.cachedDijkstras[src][i].AddVertex(src)
        dist[src] = 0

        # Find shortest paths
        for count in range(self.SizeV() - 1):
            u = self.minDistance(dist, spSet)
            spSet[u] = True
            for v in range(self.SizeV()):
                if not spSet[v] and self.adjacencyMatrix[u][v] > 0 and not dist[u] == float('inf') and dist[u] + self.adjacencyMatrix[u][v] < dist[v]:
                    dist[v] = dist[u] + self.adjacencyMatrix[u][v]
                    # A better tour was found, clear the existing tour
                    self.cachedDijkstras[src][v].clear()
                    # Make new tour by deep copying the best vertex sequence
                    for i in range(len(self.cachedDijkstras[src][u].vertexSequence)):
                        self.cachedDijkstras[src][v].InsertVertex(self.cachedDijkstras[src][u].vertexSequence[i])
                    self.cachedDijkstras[src][v].InsertVertex(v)
                
    def SolveAndCacheShortestPaths(self):
        # Solve dijkstras
        for v in range(self.SizeV()):
            self.Dijkstras(v)
            # Store connected edges
            edges = []
            for e in range(self.SizeE()):
                vertices = self.GetEdgeVertices(e)
                if vertices[0] == v or vertices[1] == v:
                    edges.append(e)
            self.connectedEdges.append(edges)
        return