
from tweetTransform import removeFile
#from geopy.distance import vincenty
from numpy import ndarray
import numpy as np

###############################################################################

def similarityCoord(summaryParsedCoord, summarySimilarityCoord): # TODO implement in C for speed
    print( "Counting distances of coords..." )
    removeFile(summarySimilarityCoord)

    # run C code for similarity
    from ctypes import cdll
    lib = cdll.LoadLibrary('./cmake_tfidf/libtfidf.so')
    lib.CountCoordinateSimilarity(summaryParsedCoord, summarySimilarityCoord)

############################################################################### 

