import numpy
import math
import random

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import os

from scipy import interpolate

class Tour:
    def __init__(self, gph):
        # variables
        self.graph = gph
        self.vertexSequence = []
        self.edgeSequence = []
        self.cost = 0
        self.ax = None

    def clear(self):
        self.vertexSequence.clear()
        self.edgeSequence.clear()
        self.cost = 0

    def plot(self, ax, col):
        # plot the tours
        offset = 0
        x = []
        y = []
        for v in range(len(self.vertexSequence)):
            vertex = self.vertexSequence[v]
            x.append(self.graph.vertices[vertex][0] + random.uniform(-offset, offset))
            y.append(self.graph.vertices[vertex][1] + random.uniform(-offset, offset))
            if v < len(self.vertexSequence) - 1:
                # pull the tours close to the edge
                x.append(self.graph.vertices[vertex][0] + ((self.graph.vertices[self.vertexSequence[v + 1]][0] - self.graph.vertices[vertex][0]) * 0.25))
                y.append(self.graph.vertices[vertex][1] + ((self.graph.vertices[self.vertexSequence[v + 1]][1] - self.graph.vertices[vertex][1]) * 0.25))

                x.append(self.graph.vertices[vertex][0] + ((self.graph.vertices[self.vertexSequence[v + 1]][0] - self.graph.vertices[vertex][0]) * 0.5))
                y.append(self.graph.vertices[vertex][1] + ((self.graph.vertices[self.vertexSequence[v + 1]][1] - self.graph.vertices[vertex][1]) * 0.5))
                
                x.append(self.graph.vertices[vertex][0] + ((self.graph.vertices[self.vertexSequence[v + 1]][0] - self.graph.vertices[vertex][0]) * 0.75))
                y.append(self.graph.vertices[vertex][1] + ((self.graph.vertices[self.vertexSequence[v + 1]][1] - self.graph.vertices[vertex][1]) * 0.75))
                continue
        
        #create interpolated lists of points
        #f, u = interpolate.splprep([x, y], s=0.1, per=True)
        #xint, yint = interpolate.splev(np.linspace(0, 1, 500), f)
        ax.plot(x, y, color = col, linewidth=2, label='length: ' + str(round(self.cost, 2)))
        
        plt.legend(loc='upper left')

        # plot the start and end node
        ax.scatter(self.graph.vertices[self.vertexSequence[0]][0], self.graph.vertices[self.vertexSequence[0]][1], marker = "*", color='red', zorder=9999)
        ax.scatter(self.graph.vertices[self.vertexSequence[0]][0], self.graph.vertices[self.vertexSequence[len(self.vertexSequence) -1 ]][1], marker = "*", color='red', zorder=9999)
        return

    def View(self, id, color):
        fig, ax = plt.subplots(1, figsize=(12, 4))
        ax.title.set_text(self.graph.name + ' tour ' + str(id))
        self.graph.plot(ax, False, False)
        self.plot(ax, color)
        # make custom legend with route information
        #tour_length = mlines.Line2D(color=color, label='length: ' + str(round(self.cost, 2)))
        plt.show(block=False)
        return ax


    def GraphExists(self):
        if self.graph == None:
            print("Trying to access a graph that has not been specified.")
            return False
        return True

    def to_string(self, delimiter = " ", ending = '\n'):
        out = "t(" + str(self.cost) + ") : v["
        for i in range(len(self.vertexSequence)):
            out += str(self.vertexSequence[i])
            if (i < len(self.vertexSequence) - 1):
                out += delimiter
            
        out += "] e["
        for i in range(len(self.edgeSequence)):
            out += str(self.edgeSequence[i])
            if (i < len(self.edgeSequence) - 1):
                out += delimiter
        out += "]" + ending
        return out
    
    def save(self, path):
        f = open(path, "a")
        f.write(self.to_string())
        f.close()
    
    # Force insert the vertex. This will not resolve issues in the tour (ie intermediate edges)
    def InsertVertex(self, vertexId):
        if (len(self.vertexSequence) == 0 and len(self.edgeSequence) == 0):
            self.vertexSequence.append(vertexId)
        elif (len(self.vertexSequence) > 0 and len(self.edgeSequence) == 0 and vertexId != self.vertexSequence[len(self.vertexSequence) - 1]):
            self.edgeSequence.append(self.graph.GetEdge(vertexId, self.vertexSequence[len(self.vertexSequence) - 1]))
            self.vertexSequence.append(vertexId)
            self.cost += self.graph.GetEdgeCost(self.edgeSequence[len(self.edgeSequence) - 1])
        elif (len(self.vertexSequence) > 0 and len(self.edgeSequence) > 0 and vertexId != self.vertexSequence[len(self.vertexSequence) - 1]):
            self.edgeSequence.append(self.graph.GetEdge(vertexId, self.vertexSequence[len(self.vertexSequence) - 1]))
            self.vertexSequence.append(vertexId)
            self.cost += self.graph.GetEdgeCost(self.edgeSequence[len(self.edgeSequence) - 1])

    def InjectShortestPathToVertex(self, vertex, shortestPath):
        for i in range(len(shortestPath.vertexSequence)):
            self.AddVertex(shortestPath.vertexSequence[i])

    def HandleFirstVertexNoEdges(self, vertex):
        self.vertexSequence.append(vertex)
        return

    def HandleFirstVertexOneEdge(self, vertex):
        self.vertexSequence.append(vertex)
        self.vertexSequence.append(self.graph.GetOppositeVertexOnEdge(vertex, self.edgeSequence[len(self.edgeSequence) - 1]))

    def HandleSecondVertexNoEdges(self, vertex):
        if (vertex != self.vertexSequence[len(self.vertexSequence) - 1]):
            self.edgeSequence.append(self.graph.GetEdge(self.vertexSequence[len(self.vertexSequence) - 1], vertex))
            self.cost += self.graph.GetEdgeCost(self.edgeSequence[len(self.edgeSequence) - 1])
            self.vertexSequence.append(vertex)
        return

    def HandleAllOtherVertexCases(self, vertex):
        if (vertex != self.vertexSequence[len(self.vertexSequence) - 1]):
            if (self.graph.IsValidEdge(self.vertexSequence[len(self.vertexSequence) - 1], vertex)):
                edge = self.graph.GetEdge(self.vertexSequence[len(self.vertexSequence) - 1], vertex)
                self.edgeSequence.append(edge)
                self.vertexSequence.append(vertex)
                self.cost += self.graph.GetEdgeCost(edge)
            else:
                self.InjectShortestPathToVertex(vertex, self.graph.GetShortestTourBetweenVertices(self.vertexSequence[len(self.vertexSequence) - 1], vertex))

    # Adds a vertex and resolves missing edges inbetween vertices
    def AddVertex(self, vertex):
        if (len(self.vertexSequence) == 0 and len(self.edgeSequence) == 0):
            self.HandleFirstVertexNoEdges(vertex)
        elif (len(self.vertexSequence) == 0 and len(self.edgeSequence) == 1):
            self.HandleFirstVertexOneEdge(vertex)
        elif (len(self.vertexSequence) == 1 and len(self.edgeSequence) == 0):
            self.HandleAllOtherVertexCases(vertex)
        elif (len(self.vertexSequence) > 0 and len(self.edgeSequence) > 0):
            self.HandleAllOtherVertexCases(vertex)

    def InjectShortestTourToEdge(self, edge, shortestPath):
        for i in range(len(shortestPath.edgeSequence)):
            self.AddEdge(shortestPath.edgeSequence[i])
        self.AddEdge(edge)

    def HandleFirstEdgeNoStartingVertex(self, edge):
        self.edgeSequence.append(edge)
        self.cost += self.graph.GetEdgeCost(edge)

    def HandleFirstEdgeWithStartingVertex(self, edge):
        vertices = self.graph.GetEdgeVertices(edge)
        if (not (vertices[0] == self.vertexSequence[len(self.vertexSequence) - 1] or vertices[1] == self.vertexSequence[len(self.vertexSequence) - 1])):
            self.InjectShortestTourToEdge(edge, self.graph.GetShortestTourBetweenVertexAndEdge(self.vertexSequence[len(self.vertexSequence) - 1], edge))
        else:
            self.edgeSequence.append(edge)
            self.vertexSequence.append(self.graph.GetOppositeVertexOnEdge(self.vertexSequence[len(self.vertexSequence) - 1], edge))
            self.cost += self.graph.GetEdgeCost(edge)

    def HandleSecondEdgeNoStartingVertex(self, edge):
        connectingVertex = self.graph.GetEdgesConnectingVertex(edge, self.edgeSequence[len(self.edgeSequence) - 1])
        if connectingVertex == -1:
            self.InjectShortestTourToEdge(edge, self.graph.GetShortestTourBetweenEdges(self.edgeSequence[len(self.edgeSequence) - 1], edge))
        else:
            startVertex = self.graph.GetOppositeVertexOnEdge(connectingVertex, self.edgeSequence[len(self.edgeSequence) - 1])
            self.vertexSequence.append(startVertex)
            self.vertexSequence.append(connectingVertex)
            self.edgeSequence.append(edge)
            self.vertexSequence.append(self.graph.GetOppositeVertexOnEdge(connectingVertex, self.edgeSequence[len(self.edgeSequence) - 1]))
            self.cost += self.graph.GetEdgeCost(edge)

    def HandleAllOtherEdgeCases(self, edge):
        connectingVertex = self.graph.GetEdgesConnectingVertex(edge, self.edgeSequence[len(self.edgeSequence) - 1])
        if (connectingVertex == -1):
            self.InjectShortestTourToEdge(edge, self.graph.GetShortestTourBetweenEdges(self.edgeSequence[len(self.edgeSequence) - 1], edge))
        else:
            if (edge != self.edgeSequence[len(self.edgeSequence) - 1]):
                sharedVertex = self.graph.GetEdgesConnectingVertex(self.edgeSequence[len(self.edgeSequence) - 1], edge)
                if (sharedVertex != self.vertexSequence[len(self.vertexSequence) - 1]):
                    if not self.graph.IsValidEdge(self.vertexSequence[len(self.vertexSequence) - 1], sharedVertex):
                        print("Issues have arrised")
                    self.vertexSequence.append(sharedVertex)
                    self.cost += self.graph.GetEdgeCost(self.edgeSequence[len(self.edgeSequence) - 1])
                    self.edgeSequence.append(self.edgeSequence[len(self.edgeSequence) - 1])

            # add any other edge
            oppositeVertex = self.graph.GetOppositeVertexOnEdge(self.vertexSequence[len(self.vertexSequence) - 1], edge)
            if not self.graph.IsValidEdge(self.vertexSequence[len(self.vertexSequence) - 1], oppositeVertex):
                print("Issues have arrised")
            self.vertexSequence.append(oppositeVertex)
            self.edgeSequence.append(edge)
            self.cost += self.graph.GetEdgeCost(edge)

    # Adds a edge and resolves the path
    def AddEdge(self, edge):
        if (len(self.vertexSequence) == 0 and len(self.edgeSequence) == 0):
            self.HandleFirstEdgeNoStartingVertex(edge)
        elif (len(self.vertexSequence) == 1 and len(self.edgeSequence) == 0):
            self.HandleFirstEdgeWithStartingVertex(edge)
        elif (len(self.vertexSequence) == 0 and len(self.edgeSequence) == 1):
            self.HandleSecondEdgeNoStartingVertex(edge)
        else:
            self.HandleAllOtherEdgeCases(edge)

    def GetEdgePath(self):
        return self.edgeSequence

    def GetVertexPath(self):
        return self.vertexSequence