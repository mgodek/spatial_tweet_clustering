from __future__ import absolute_import, print_function

import sys, os, signal, time
import tweetFetcher
import clusterModule
import tweetTransform

import numpy as np
from tweetTransform import stemData, tfidfData, makeMatrixFiles
from clusterModule import setupCluster, clusterClara, clusterResults
from time import gmtime, strftime

from time import gmtime, strftime

pathToRawTweets        = "tweets/"
pathToStemmedTweets    = "tweetsStemmed.txt"
tweetsMatrixFile       = "claraTweetsMatrixFile.txt"  # matrix with each row being a set of ints
tweetsFeatureListFile  = "claraTweetsFeatureList.txt" # mapping between stemmed features and ints
clusterNaiveResultFile = "claraOutputNaive.txt"
clusterLessNResultFile = "claraOutputLessN.txt"

def signal_handler(signal, frame):
	print('You pressed Ctrl+C!')
	#sys.exit(0)
	main_menu()

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

menu_actions  = {}

def exec_menu(choice):
    os.system('clear')
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

def fetchTweetsMenu():
    amount = 1000
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

def transformTweetDataMenu():
    print ( "Transforming raw json tweets to R input" )

    print ( "Stem raw data? Y/n" )
    choice = raw_input(" >>  ")
    if choice == 'Y':
        stemData(pathToRawTweets, pathToStemmedTweets)

    print ( "TFIDF stemmed data? Y/n" )
    choice = raw_input(" >>  ")
    if choice == 'Y':
        tfidfData(pathToStemmedTweets)

    makeMatrixFiles(pathToStemmedTweets, tweetsMatrixFile, tweetsFeatureListFile)    

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

def clusterTweetsNaiveMenu():
    print ("Clustering tweets with Clara - naive approach !")

    print ("How many clusters do You want to create?")
    k = raw_input(" >>  ")

    clusterClara(tweetsMatrixFile, k, clusterNaiveResultFile)

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

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

def viewResultsMenu():
    print ("Viewing results !")

    clusterResults(clusterNaiveResultFile)
    clusterResults(clusterLessNResultFile)

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

def back():
    menu_actions['main_menu']()

def exit():
    sys.exit()
 
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
    main_menu()
