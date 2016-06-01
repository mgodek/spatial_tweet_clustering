
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
from clusterModule import setupCluster, clusterClara, clusterResults
from time import gmtime, strftime
from similarity import similarityCoord

summaryRawTweets       = 'summaryRawTweets.txt'
summarySimilarityCoord = 'summarySimilarityCoord.txt'
summaryParsedCoord     = 'summaryParsedCoord.txt'
summaryParsedTweets    = 'summaryParsedTweets.txt'
summaryStemmedTweets   = 'summaryStemmedTweets.txt'
summaryTfidfTweets     = 'summaryTfidfTweets.txt'
summaryStopWords       = 'summaryTfidfStopWords.txt'
summaryDictionaryFile  = 'summaryTfidfDictionary.txt'
tweetsMatrixFile       = "summaryClaraTweetsMatrixFile.txt"  # matrix with each row being a set of weights (column position indicated feature)
clusterNaiveResultFile = "claraOutputNaive.txt"
clusterLessNResultFile = "claraOutputLessN.txt"

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
    print ("3. Fetch tweets periodically")
    print ("4. Parse and stem tweets")
    print ("5. Tfidf stemmed tweets")
    print ("6. Cluster tweets using all data")
    print ("7. Cluster tweets using location data")
    print ("8. View results")
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

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################

def fetchTweetsMenu():
    amount = 30000
    print ("How much tweets to fetch? default=%d " % amount )
    amountRead = raw_input(" >>  ")
    try:
        amount = int(amountRead)
    except ValueError:
        amount = 30000

    removeOldTweets = "n"
    print ("Remove previous tweets? y/n default=%s " % removeOldTweets )
    removeOldTweets = raw_input(" >>  ")
    if removeOldTweets == "y":
        removeFile(summaryRawTweets)

    print ("Fetching ", amount, " tweets !")
    
    try:
        tweetFetcher.fetchTweets(summaryRawTweets, amount)
    except KeyboardInterrupt, e:
        print( "Interrupted" )
    
    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################
 
def fetchTweetsPeriodicallyMenu():
    amount = 20000
    hours = 1
    times = 12
    print ("Fetching ", amount, " tweets periodically every ", hours, " hours!")
    strftime("%Y-%m-%d %H:%M:%S", gmtime())

    removeFile(summaryRawTweets)

    for x in range(1, times):
        print( "Round ", x, " out of ", times )
        try:
            tweetFetcher.fetchTweets(summaryRawTweets, amount)
        except KeyboardInterrupt, e:
            print( "Interrupted" )

	if x + 1 < times:
            print( "Waiting ", hours, " hours for round ", x+1, " out of ", times )
            time.sleep(3600*hours)


    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################

def parseTweetDataMenu():
    print ( "Parsing and stemming raw json tweets" )

    global interactive

    onlySpdbData = False

    print ( "Use only location data? y/n. Default n." )
    choice = raw_input(" >>  ")
    if choice == 'y':
         onlySpdbData = True

    parseData(onlySpdbData, summaryRawTweets, summaryParsedTweets)

    stemData(summaryParsedTweets, summaryStemmedTweets)

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################

def tfIdfTweetDataMenu():
    print ( "Tfidfing parsed json tweets to R input" )

    global interactive

    thresholdBottom = float(0.01)
    thresholdUpper  = float(100)
    stopWordCountBottom = 17
    sampleRatio = 0.3
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

        print ( "Specify sampleRatio? default=%s. Enter 1 to turn it off." % str(sampleRatio) )
        choice = raw_input(" >>  ")
        if choice != '':
            sampleRatio=float(choice)


    tfidfData(summaryStemmedTweets, summaryTfidfTweets, summaryStopWords,
              summaryDictionaryFile, thresholdUpper, thresholdBottom,
              stopWordCountBottom, sampleRatio)

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################

def clusterTweetsAllDataMenu():
    print ("Clustering tweets with Clara using all available data") 

    print ( "Making matrix file" )
    makeClusterMatrixFile(summaryTfidfTweets, tweetsMatrixFile)   

    k = 7
    print ("How many clusters do You want to create? (default=%d)" % k )
    kRead = raw_input(" >>  ")
    try:
        k = int(kRead)
    except ValueError:
        k = 7

    clusterClara(tweetsMatrixFile, k, clusterNaiveResultFile)

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################

def clusterTweetsCoordinatesMenu():
    print ("Clustering tweets with Clara using only coordinate data")

    print ( "Making matrix file" )
    extractCoord(summaryParsedTweets, summaryParsedCoord)
    makeClusterMatrixFile(summaryParsedCoord, tweetsMatrixFile)

    #print ( "Calculate distances of tweets? y/n. Default n." )
    #choice = raw_input(" >>  ")
    #if choice == 'y':
    #    similarityCoord(summaryParsedCoord, summarySimilarityCoord)

    k = 7
    print ("How many clusters do You want to create? (default=%d)" % k )
    kRead = raw_input(" >>  ")
    try:
        k = int(kRead)
    except ValueError:
        k = 7

    clusterClara(tweetsMatrixFile, k, clusterLessNResultFile)

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################

def viewResultsMenu():
    print ("Viewing results !")

    k = 0
    print ("To see clustered coordinate data result only enter 0. 1 for the other. (default=%d)" % k )
    kRead = raw_input(" >>  ")
    try:
        k = int(kRead)
    except ValueError:
        k = 0

    if k == 0:
        displayResultsOnMap(summaryParsedCoord, clusterLessNResultFile, "Tweets' coordinate data")
    else:
        displayResultsOnMap(summaryParsedCoord, clusterNaiveResultFile, "Tweets' all data")

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
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
    '3': fetchTweetsPeriodicallyMenu,
    '4': parseTweetDataMenu,
    '5': tfIdfTweetDataMenu,
    '6': clusterTweetsAllDataMenu,
    '7': clusterTweetsCoordinatesMenu,
    '8': viewResultsMenu,
    '9': back,
    '0': exit,
}

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    global interactive
    interactive = False
    for x in sys.argv[1:]:
        if x == "i":
            interactive = True

    main_menu()

###############################################################################

