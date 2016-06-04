
from tweetTransform import removeFile
#from geopy.distance import vincenty
from numpy import ndarray
import numpy as np
from cmath import log10

###############################################################################

def distanceMedoid(tweetAttributeFileName, medoidFileName, distanceFileName):
    print("Counting distance from medoids using %s %s %s" % (tweetAttributeFileName,medoidFileName, distanceFileName) )
    
    tweetAttributeFile = open(tweetAttributeFileName, 'r')
    medoidFile = open(medoidFileName, 'r')

    removeFile(distanceFileName) 
    distanceFile = open(distanceFileName, 'w')

    attributesLine = medoidFile.readline() # ignore attributes names

    # read medoids to 2d array : groups/attributes
    groupCollection = []
    groupIdx = 0
    for line in medoidFile:
        #skip row name
        line = line.split(' ', 1)[1]

        #split attributes
        featureCollection = line.split(' ')

        medoidCollection = ndarray((len(featureCollection),1),float)
        # get medoid of each attribute to column. each row is a group
        for attributeIdx in range(0, len(featureCollection)):
            medoidCollection[attributeIdx] = float(' '.join(featureCollection[attributeIdx].split()))

        groupIdx += 1
        groupCollection.append(medoidCollection)

    #print(groupCollection)

    # count distances to medoids
    for line in tweetAttributeFile:
        #skip row name
        line = line.split(' ', 1)[1]

        #split attributes
        featureCollection = line.split(' ')

        attributes = ndarray((len(featureCollection),1),float)
        # calc distance of each attribute of a row (sample tweet) from each medoid column
        for attributeIdx in range(0, len(featureCollection)):
            attributes[attributeIdx] = float(' '.join(featureCollection[attributeIdx].split()))

        distanceVec = ndarray((len(groupCollection),len(featureCollection)),float)
        for i in range(0, len(groupCollection)):
            distanceVec[i] = np.linalg.norm(attributes-groupCollection[i])
        #print(distanceVec)
        distance = 0
        for i in range(0, len(distanceVec)):
            distance += log10(distanceVec[i][0]+1) # need to move from zero a bit for log
        
        distanceFile.write("nothing " + str(distance)+"\n")

    tweetAttributeFile.close()
    medoidFile.close()
    distanceFile.close()

###############################################################################

def similarityCoord(summaryParsedCoord, summarySimilarityCoord):
    print( "Counting distances of coords..." )
    removeFile(summarySimilarityCoord)

    # run C code for similarity
    from ctypes import cdll
    lib = cdll.LoadLibrary('./cmake_tfidf/libtfidf.so')
    lib.CountCoordinateSimilarity(summaryParsedCoord, summarySimilarityCoord)

############################################################################### 

