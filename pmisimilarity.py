import math

"""Pointwise Mutual Information"""

def pmi(x, y, xy):
    return math.log2((xy / x) / y)

def npmi(xy, pmi):
    return pmi / math.log2(xy)

def calculateSimilarity(D, f1, f2, f12):
    """
    calculates the PMI similarity
    """
    x = (f1 + 1) / (D + 1)
    y = (f2 + 1) / (D + 1)
    xy = (f12 + 1) / (D + 1)
    result = npmi(xy, pmi(x, y, xy))
    return result
