
from tweetTransform import removeFile
#from geopy.distance import vincenty
from numpy import ndarray
import numpy as np

###############################################################################

def similarityCoord(summaryParsedCoord, summarySimilarityCoord): # TODO implement in C for speed
    print( "Counting distances of coords..." )
    removeFile(summarySimilarityCoord)

    fOut = open(summarySimilarityCoord, 'w')
    fIn = open(summaryParsedCoord, 'r')

    rowCount=0
    for line in fIn:
        rowCount = rowCount + 1
    fIn.close()
    fIn = open(summaryParsedCoord, 'r')

    coordMat = ndarray((rowCount,2),int)
    rowIndex = 0
    for line in fIn:
        #id_str_json = line.split(' ', 1)[0]
        longitude = int(line.split(' ', 2)[1])
        latitude = int(line.split(' ', 2)[2])
        #print( "id_str_json=%s longitude=%d latit11ude=%d" % (id_str_json,longitude,latitude) )
        coordMat[rowIndex, 0] = latitude
        coordMat[rowIndex, 1] = longitude

        rowIndex = rowIndex + 1

    for r in range(0, rowCount):
        for c in range(0, rowCount-r):
            #distance = int( vincenty((coordMat[r,0], coordMat[r,1]), (coordMat[c,0], coordMat[c,1])).miles )
            a = np.array(coordMat[r,0], coordMat[r,1])
            b = np.array(coordMat[c,0], coordMat[c,1])
            distance = int(np.linalg.norm(a-b))
            #print( "distance %d(%d %d):%d(%d %d) = %s" %(r,coordMat[r,0], coordMat[r,1],c,coordMat[c,0], coordMat[c,1],distance) )
            fOut.write(str(r)+' '+str(c)+' '+str(distance)+'\n')

    print( "Change to cosine distance..." ) #TODO 1 - x/max. same will have 1 value. distant will have 0

    fIn.close()
    fOut.close()

############################################################################### 

