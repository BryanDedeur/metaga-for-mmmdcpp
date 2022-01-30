import matplotlib.pyplot as plt
import numpy as np

class Statistics:
    def __init__(self):
        self.sum = 0
        self.min = float('inf')
        self.max = 0
        self.count = 0

    def clear(self):
        self.sum = 0
        self.min = float('inf')
        self.max = 0
        self.count = 0
            
    def addValue(self, value):
        self.sum += value
        self.count += 1
        if value < self.min:
            self.min = value
        if value > self.max:
            self.max = value 

    def mean(self):
        return self.sum / self.count
    
    def ave(self):
        return self.mean()
    
    def total(self):
        return self.sum

    def to_string(self, delimiter = ',', ending = '\n'):
        data = [
            self.mean(),
            self.count,
            self.min,
            self.max
            ]
        formatted = ''
        for i in range(len(data)):
            formatted += str(data[i])
        if i < len(data) - 1:
            formatted += delimiter
        else:
            formatted += ending
        return formatted

    def save(self, filepath):
        f = open(filepath, "a")
        f.write(self.to_string())
        f.close()
        return
