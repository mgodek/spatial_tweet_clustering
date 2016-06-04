
###############################################################################

from __future__ import absolute_import, print_function
import shutil
import sys, os, signal, time
import tweetFetcher
import clusterModule
import tweetTransform
import numpy as np
from clusterView import displayResultsOnMap
from tweetTransform import parseData, stemData, tfidfData, makeClusterMatrixFile, extractCoord, removeFile
from clusterModule import setupCluster, clusterClara, clusterResultsRandIdx
from time import gmtime, strftime
from similarity import similarityCoord
import re
import time

dataRawTweetsPrefix       = 'dataRawTweets'
dataSimilarityCoordPrefix = 'dataSimilarityCoord'
dataParsedCoordPrefix     = 'dataParsedCoord'
dataParsedTweetsPrefix    = 'dataParsedTweets'
dataStemmedTweetsPrefix   = 'dataStemmedTweets'
dataTfidfTweetsPrefix     = 'dataTfidfTweets'
dataFeatureFilePrefix     = 'dataTfidfFeatures'
dataStopWordsPrefix       = 'dataTfidfStopWords'
dataDictionaryFilePrefix  = 'dataTfidfDictionary'
dataTweetsMatrixFilePrefix= "dataClaraTweetsMatrixFile"
dataClusterFilePrefix     = "dataClusteredOutput"
dataClusterTypeInfixLength= 3
dataMedoidsFilePrefix     = "dataMedoidsOutput"

###############################################################################

def readStr(message, defaultStr):
    value = raw_input("%s >> %s" % (message, defaultStr))
    try:
        return defaultStr+str(value)
    except ValueError:
        return defaultStr

###############################################################################

def readInt(message, defaultInt):
    value = raw_input("%s default=%d >> " % (message, defaultInt))
    try:
        return int(value)
    except ValueError:
        return defaultInt

###############################################################################

def readFileName(message, defaultFileNamePrefix):
    newFileName = defaultFileNamePrefix
    filePrefixCollection = []
    for file in os.listdir(os.getcwd()):
        if defaultFileNamePrefix in file:
            filePrefixCollection.append(file)
    if len(filePrefixCollection) > 0:
        print( "Existing: %s" % ', '.join(filePrefixCollection) )

    newFileName = readStr(message, newFileName)
    try:
        return str(newFileName)
    except ValueError:
        return defaultFileNamePrefix

###############################################################################

def chooseFile(fileNamePrefix, action):
    dataCollection = []
    for file in os.listdir(os.getcwd()):
        if fileNamePrefix in file:
            dataCollection.append(file)

    if len(dataCollection) == 0:
        print( "No data with prefix %s available. Early return." % fileNamePrefix )
        return

    dataCollectionArrayStr = ""
    for i in range(0,len(dataCollection)):
        dataCollectionArrayStr += ("[" + str(i) + "]" + dataCollection[i] + " ")
    i = readInt(str("Which do You want to %s? %s" % (action, dataCollectionArrayStr)), 0)
    return dataCollection[i]

###############################################################################

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    #sys.exit(0)
    main_menu()

###############################################################################

def main_menu():
    #os.system('clear')
    
    print ("Please choose the function you want to start:")
    print ("1. Run setup")
    print ("2. Fetch tweets")
    print ("3. Parse and stem tweets")
    print ("4. Tfidf stemmed tweets")
    print ("5. Cluster tweets using only location data")
    print ("6. Cluster tweets using all data in same way")
    print ("7. Cluster tweets using location and text")
    print ("8. View results")
    print ("9. View Rand Index")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
 
    return

###############################################################################

menu_actions  = {}

###############################################################################

def exec_menu(choice):
    #os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print ("Wrong selection, please try again.")
            menu_actions['main_menu']()
    return

###############################################################################

def setup():
    print ( "Running setup" )
    
    if os.getuid() == 0:
        setupCluster()
    else:
	print ("This program is not run as sudo so this function will not work")

    main_menu()
    return

###############################################################################

def fetchTweetsMenu():
    newRawTweetsName = readFileName("How to name the tweet file?", dataRawTweetsPrefix)

    amount = readInt("How much tweets to fetch?", 30000)
    times = readInt("How many times to repeat?", 1)
    hours = readInt("How many hours to wait in between?", 1)
    print ("Fetching %d times %d tweets periodically every %d hours." % (times, amount, hours))
    strftime("%Y-%m-%d %H:%M:%S", gmtime())

    for x in range(0, times):
        start = time.time()
        print( "Round ", x+1, " out of ", times )
        try:
            tweetFetcher.fetchTweets(newRawTweetsName, amount)
        except KeyboardInterrupt, e:
            print( "Interrupted" )

        waitTime = 3600*hours - (time.time() - start)
	if x + 1 < times:
            print( "Waiting ", float(int(waitTime/36))/100, " hours for next round ", x+2, " out of ", times )
            time.sleep(waitTime)
    
    main_menu()
    return

###############################################################################

def parseTweetDataMenu():
    rawDataCollection = []
    for file in os.listdir(os.getcwd()):
        if dataRawTweetsPrefix in file:
            rawDataCollection.append(file)

    rawTweetsFileName = chooseFile(dataRawTweetsPrefix, "parse")

    #print ( "Use only location data? y/n. Default n." )
    #choice = raw_input(" >>  ")
    #if choice == 'y':
    #     onlySpdbData = True

    onlySpdbData = False
    parsedTweetsFileName = dataParsedTweetsPrefix+(rawTweetsFileName[len(dataRawTweetsPrefix):])

    parseData(onlySpdbData, rawTweetsFileName, parsedTweetsFileName+"_noSPDB", False)
    stemData(parsedTweetsFileName+"_noSPDB", dataStemmedTweetsPrefix+parsedTweetsFileName[len(dataParsedTweetsPrefix):]+"_noSPDB")

    parseData(onlySpdbData, rawTweetsFileName, parsedTweetsFileName+"_withSPDB", True)
    stemData(parsedTweetsFileName+"_withSPDB", dataStemmedTweetsPrefix+parsedTweetsFileName[len(dataParsedTweetsPrefix):]+"_withSPDB")

    # run it twice to have 2 file for each branch: with and without SPDB prefix
    extractCoord(parsedTweetsFileName+"_withSPDB", 
                 dataParsedCoordPrefix+parsedTweetsFileName[len(dataParsedTweetsPrefix):]+"_withSPDB")
    extractCoord(parsedTweetsFileName+"_withSPDB", 
                 dataParsedCoordPrefix+parsedTweetsFileName[len(dataParsedTweetsPrefix):]+"_noSPDB")

    main_menu()
    return

###############################################################################

def tfIdfTweetDataMenu():
    stemmedTweetsFileName = chooseFile(dataStemmedTweetsPrefix, "tfidf")

    global interactive

    thresholdBottom = float(0.01)
    thresholdUpper  = float(100)
    stopWordCountBottom = 17
    if interactive == True:
        print ( "Specify threshold bottom? default=%s. Enter 0 to turn it off." % str(thresholdBottom) )
        choice = raw_input(" >>  ")
        if choice != '':
            thresholdBottom=float(choice)

        print ( "Specify threshold upper? default=%s. Enter 100 to turn it off." % str(thresholdUpper) )
        choice = raw_input(" >>  ")
        if choice != '':
            thresholdUpper=float(choice)

        print ( "Specify stopWordCount bottom? default=%d. Enter 0 to turn it off." % stopWordCountBottom )
        choice = raw_input(" >>  ")
        if choice != '':
            stopWordCountBottom=int(choice)

    tfidfData(stemmedTweetsFileName,
              dataTfidfTweetsPrefix   +stemmedTweetsFileName[len(dataStemmedTweetsPrefix):],
              dataStopWordsPrefix     +stemmedTweetsFileName[len(dataStemmedTweetsPrefix):],
              dataDictionaryFilePrefix+stemmedTweetsFileName[len(dataStemmedTweetsPrefix):],
              dataFeatureFilePrefix   +stemmedTweetsFileName[len(dataStemmedTweetsPrefix):],
              thresholdUpper, thresholdBottom, stopWordCountBottom)

    main_menu()
    return

###############################################################################

def clusterTweetsAllDataMenu():
    print ("Clustering tweets with Clara using all available data in same way") 
    fileResults = chooseFile(dataParsedTweetsPrefix, "cluster results" )
    if len(fileResults) == 0:
        return

    print ( "Making matrix file" )
    matrixFileName = dataTweetsMatrixFilePrefix+fileResults[len(dataParsedTweetsPrefix):]
    makeClusterMatrixFile(dataFeatureFilePrefix+fileResults[len(dataParsedTweetsPrefix):], matrixFileName)

    k = readInt("How many clusters do You want to create?", 7)

    clusterClara(matrixFileName, k,
                 dataClusterFilePrefix+"_6_"+fileResults[len(dataParsedTweetsPrefix):],
                 dataMedoidsFilePrefix+"_6_"+fileResults[len(dataParsedTweetsPrefix):])

    main_menu()
    return

###############################################################################

def clusterTweetsLocTextMenu():
    print ("Clustering tweets with Clara using two feature vectors: location and text")
    fileResults = chooseFile(dataParsedTweetsPrefix, "cluster results" )
    if len(fileResults) == 0:
        return

   #TODO

    k = readInt("How many clusters do You want to create?", 7)

    clusterClara(matrixFileName, k,
                 dataClusterFilePrefix+"_7_"+fileResults[len(dataParsedTweetsPrefix):],
                 dataMedoidsFilePrefix+"_7_"+fileResults[len(dataParsedTweetsPrefix):])

    main_menu()
    return

###############################################################################

def clusterTweetsCoordinatesMenu():
    print ("Clustering tweets with Clara using only coordinate data")
    fileResults = chooseFile(dataParsedTweetsPrefix, "cluster results" )
    if len(fileResults) == 0:
        return

    print ( "Making matrix file" )
    matrixFileName = dataTweetsMatrixFilePrefix+fileResults[len(dataParsedTweetsPrefix):]
    makeClusterMatrixFile(dataParsedCoordPrefix+fileResults[len(dataParsedTweetsPrefix):], 
                          matrixFileName)

    #print ( "Calculate distances of tweets? y/n. Default n." )
    #choice = raw_input(" >>  ")
    #if choice == 'y':
    #    similarityCoord(summaryParsedCoord, summarySimilarityCoord)

    k = readInt("How many clusters do You want to create?", 7)

    clusterClara(matrixFileName, k, 
                 dataClusterFilePrefix+"5"+fileResults[len(dataParsedTweetsPrefix):],
                 dataMedoidsFilePrefix+"5"+fileResults[len(dataParsedTweetsPrefix):])

    main_menu()
    return

###############################################################################

def viewResultsMenu():
    fileResults = chooseFile(dataClusterFilePrefix, "view results" )
    if len(fileResults) == 0:
        return

    displayResultsOnMap(dataParsedCoordPrefix+fileResults[len(dataClusterFilePrefix)+dataClusterTypeInfixLength:], fileResults, "Tweets data")

    main_menu()
    return

###############################################################################

def viewRandMenu():
    fileResults1 = chooseFile(dataClusterFilePrefix, "choose as first cluster result for rand index input" )
    if len(fileResults1) == 0:
        return

    fileResults2 = chooseFile(dataClusterFilePrefix, "choose as second cluster result for rand index input" )
    if len(fileResults2) == 0:
        return

    clusterResultsRandIdx(fileResults1, fileResults2)
    main_menu()
    return

###############################################################################

def back():
    menu_actions['main_menu']()

###############################################################################

def exit():
    sys.exit()

###############################################################################
 
# Menu definition
menu_actions = {
    'main_menu': main_menu,
    '1': setup,
    '2': fetchTweetsMenu,
    '3': parseTweetDataMenu,
    '4': tfIdfTweetDataMenu,
    '5': clusterTweetsCoordinatesMenu,
    '6': clusterTweetsAllDataMenu,
    '7': clusterTweetsLocTextMenu,
    '8': viewResultsMenu,
    '9': viewRandMenu,
    '0': exit,
}

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    global interactive
    interactive = False
    for x in sys.argv[1:]:
        if x == "i":
            interactive = True
        if x == "init":
            setupCluster()
            exit()

    main_menu()

###############################################################################

