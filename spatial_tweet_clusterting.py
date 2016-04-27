from __future__ import absolute_import, print_function

import sys, os

import tweetFetcher

import signal

import time

import subprocess

def signal_handler(signal, frame):
	print('You pressed Ctrl+C!')
        #sys.exit(0)
	main_menu()

def main_menu():
    os.system('clear')
    
    print ("Please choose the function you want to start:")
    print ("1. Fetch tweets")
    print ("2. Fetch tweets periodically")
    print ("3. Cluster tweets naive")
    print ("4. Cluster tweets less naive")
    print ("5. View results")
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

    for x in range(1, times):
        print( "Round ", x, " out of ", times )
        try:
            tweetFetcher.fetchTweets(amount)
        except KeyboardInterrupt, e:
            print( "Interrupted" )

	if x + 1 < times:
            print( "Waiting ", hours, " hours for round ", x, " out of ", times )
            time.sleep(3600*hours)


    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

def clusterTweetsNaiveMenu():
    print ("Clustering tweets naive approach !")

    print ( "TODO" )

    # Define command and arguments
    command = 'Rscript'
    path2script = 'clusterNaive.R'

    # Variable number of args in a list
    args = ['11', '3', '9', '42']

    # Build subprocess command
    cmd = [command, path2script] + args

    # check_output will run the command and store to result
    x = subprocess.check_output(cmd, universal_newlines=True)

    print('The maximum of the numbers is:', x)

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

def clusterTweetsLessNaiveMenu():
    print ("Clustering tweets less naive approach !")

    print ( "TODO" )

    print ("9. Back")
    print ("0. Quit")
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

def viewResultsMenu():
    print ("Viewing results !")

    print ( "TODO" )

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
    '1': fetchTweetsMenu,
    '2': fetchTweetsPeriodicallyMenu,
    '3': clusterTweetsNaiveMenu,
    '4': clusterTweetsLessNaiveMenu,
    '5': viewResultsMenu,
    '9': back,
    '0': exit,
}

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main_menu()
