
###############################################################################

from __future__ import absolute_import, print_function
import shutil
import sys, os, signal, time
import tweetFetcher
import clusterModule
import tweetTransform
import numpy as np
from tweetTransform import parseData, stemData, tfidfData, makeMatrixFile, removeFile
from clusterModule import setupCluster, clusterClara, clusterResults
from time import gmtime, strftime

pathToRawTweets        = "tweets"
summaryParsedTweets    = "summaryParsedTweets.txt"
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
    os.system('clear')
    
    print ("Please choose the function you want to start:")
    print ("1. Run setup")
    print ("2. Fetch tweets")
    print ("3. Fetch tweets periodically")
    print ("4. Prepare tweets for clustering")
    print ("5. Cluster tweets naive")
    print ("6. Cluster tweets less naive")
    print ("7. View results")
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
    #TODO run start.sh ?
    
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
        
    print ("Fetching ", amount, " tweets !")
    
    try:
        tweetFetcher.fetchTweets(amount)
    except KeyboardInterrupt, e:
        print( "Interrupted" )
    
    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################
 
def fetchTweetsPeriodicallyMenu():
    amount = 5000
    hours = 2
    times = 12
    print ("Fetching ", amount, " tweets periodically every ", hours, " hours!")
    strftime("%Y-%m-%d %H:%M:%S", gmtime())

    for x in range(1, times):
        print( "Round ", x, " out of ", times )
        try:
            tweetFetcher.fetchTweets(amount)
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

def transformTweetDataMenu():
    print ( "Transforming raw json tweets to R input" )

    global interactive

    if interactive == True:
        print ( "Parse raw data? y/n" )
        choice = raw_input(" >>  ")
        if choice == 'y':
             parseData(pathToRawTweets, summaryParsedTweets)
    else:
        parseData(pathToRawTweets, summaryParsedTweets)

    if interactive == True:
        print ( "Stem parsed data? y/n" )
        choice = raw_input(" >>  ")
        if choice == 'y':
            stemData(summaryParsedTweets, summaryStemmedTweets)
    else:
        stemData(summaryParsedTweets, summaryStemmedTweets)

    thresholdBottom = float(0.4)
    thresholdUpper  = float(0.9)
    stopWordCountBottom = 8
    sampleRatio = 0.3
    if interactive == True:
        print ( "TFIDF stemmed data?" )
        choice = raw_input(" >>  ")
        if choice == 'y':
            print ( "Specify threshold bottom? default=%s. Enter 0 to turn it off." % str(thresholdBottom) )
            choice = raw_input(" >>  ")
            if choice != '':
                thresholdBottom=float(choice)

            print ( "Specify threshold upper? default=%s. Enter 10 to turn it off." % str(thresholdUpper) )
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
    else:
            tfidfData(summaryStemmedTweets, summaryTfidfTweets, summaryStopWords,
                      summaryDictionaryFile, thresholdUpper, thresholdBottom,
                      stopWordCountBottom, sampleRatio)

    if interactive == True:
        print ( "Make matrix? y/n" )
        choice = raw_input(" >>  ")
        if choice == 'y':
            makeMatrixFile(summaryTfidfTweets, tweetsMatrixFile)   
    else:
        makeMatrixFile(summaryTfidfTweets, tweetsMatrixFile)   

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################

def clusterTweetsNaiveMenu():
    print ("Clustering tweets with Clara - naive approach !") 

    print ("How many clusters do You want to create? (default=7)")
    kRead = raw_input(" >>  ")
    k = 7
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

def clusterTweetsLessNaiveMenu():
    print ("Clustering tweets with Clara - less naive approach !")

    print ( "TODO need to scale features!" ) #TODO

    print ("How many clusters do You want to create?")
    k = raw_input(" >>  ")

    clusterClara(tweetsMatrixFile, k, clusterLessNResultFile)

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

###############################################################################

def viewResultsMenu():
    print ("Viewing results !")

    clusterResults(clusterNaiveResultFile)
    clusterResults(clusterLessNResultFile)

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
    '4': transformTweetDataMenu,
    '5': clusterTweetsNaiveMenu,
    '6': clusterTweetsLessNaiveMenu,
    '7': viewResultsMenu,
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

