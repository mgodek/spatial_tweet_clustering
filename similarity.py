
from tweetTransform import removeFile
#from geopy.distance import vincenty
from numpy import ndarray
import numpy as np
from cmath import log10
from math import fabs

###############################################################################

def distanceMedoid(tweetAttributeFileName, medoidFileName, distanceFileName):
    print("Counting distance from medoids using %s %s %s" % (tweetAttributeFileName,medoidFileName, distanceFileName) )
    
    previousDistances = []
    # read existing distances
    try:
        distanceFile = open(distanceFileName, 'r')
        for line in distanceFile:
            previousDistances.append(line.replace('\n', ''))
        distanceFile.close()
    except IOError:
        print( "%s no previous data" % distanceFileName )

    distanceFile = open(distanceFileName, 'w')

    tweetAttributeFile = open(tweetAttributeFileName, 'r')
    medoidFile = open(medoidFileName, 'r')
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
    lineIdx = 0
    maxDist = 0.0
    minDist = float('inf') 
    currentDistances = []
    for line in tweetAttributeFile:
        #skip row name
        line = line.split(' ', 1)[1]

        #split attributes
        featureCollection = line.split(' ')

        attributes = ndarray((len(featureCollection),1),float)
        # calc distance of each attribute of a row (sample tweet) from each medoid column
        for attributeIdx in range(0, len(featureCollection)):
            attributes[attributeIdx] = float(' '.join(featureCollection[attributeIdx].split()))

        # calc distance from given point to each medoid
        distanceVec = ndarray((len(groupCollection),len(featureCollection)),float)
        for i in range(0, len(groupCollection)):
            distanceVec[i] = np.linalg.norm(attributes-groupCollection[i])
        #print(distanceVec)

        distance = 0.0
        # TODO here we try to not have circles around a europs medoid. instead try to break it
        for i in range(0, len(distanceVec)):
            for j in range(0, len(attributes)):
                multitude = 1 #+ 2*j
                if (j % 2 == 0) and (attributes[j] > groupCollection[i][j]):
                    multitude += 3 #* (attributes[j] - groupCollection[i][j])

                if (j % 2 == 1) and (attributes[j] <= groupCollection[i][j]):
                    multitude += 3 #* (groupCollection[i][j]-attributes[j])
                
                #multitude = 1 # this line makes the groups circular again
                distance += multitude*log10(distanceVec[i][j]+1) # need to move from zero a bit for log
                currentDistances.append(dinstance)
                #gathering min and max to use for normalization
                if distance > maxDist:
                    maxDist = distance
                if distance < minDist:
                    minDist = distance
                
    for distance in currentDistances: 
        #every written dinstance will be normalized
        if ( len(previousDistances) == 0 ):
            # need to have a first column with no data
            distanceFile.write("nothing " + str((distance*32 - minDist*32)/maxDist)+"\n")
        else:
            distanceFile.write(previousDistances[lineIdx] + " " + str((distance*32 - minDist*32)/maxDist)+"\n")
        lineIdx += 1

    tweetAttributeFile.close()
    medoidFile.close()
    distanceFile.close()

###############################################################################

def distanceSqrLongPlusLat(tweetAttributeFileName, distanceFileName):
    print("Counting distance by long^2+lat using %s %s" % (tweetAttributeFileName, distanceFileName) )
    
    tweetAttributeFile = open(tweetAttributeFileName, 'r')

    removeFile(distanceFileName) 
    distanceFile = open(distanceFileName, 'w')

    # count distances
    for line in tweetAttributeFile:
        #skip row name
        line = line.split(' ', 1)[1]

        #split attributes
        featureCollection = line.split(' ')

        attributes = ndarray((len(featureCollection),1),float)
        # calc distance of each attribute of a row (sample tweet) from each medoid column
        for attributeIdx in range(0, len(featureCollection)):
            attributes[attributeIdx] = float(' '.join(featureCollection[attributeIdx].split()))

        attributes[1] += 40 # make longitude on + side
        #if attributes[0] > 40: # try to chnage strips to checkers
        #    attributes[0] = -1*attributes[0]
        distance = attributes[1]*attributes[1] + attributes[0]
        
        distanceFile.write("nothing " + str(distance)+"\n")

    tweetAttributeFile.close()
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

