
from rpy2.robjects.packages import importr, data
import numpy
import re, string, timeit
import shutil
from pprint import pprint
import simplejson
import json
import os
import sys
import subprocess
from shlex import split
import random
from ctypes import *

###############################################################################

def removeFile(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

###############################################################################

class TweetsCoordinates:

    def __init__(self, isValid=False, obj=''):
        self.isValid = isValid
        if isValid == True:
            if 'coordinates' in obj :
                coor = obj['coordinates']
		self.longitude = (int(coor[0][0][0]) + 180)
		self.latitude = (int(coor[0][0][1])  + 90)
            else:
		self.isValid = False
		print ('TweetsCoordinates fail: coordinates are wrong')
		#print (obj)
		#raise Exception('Invalid object passed to TweetsCoordinates, cannot intialize')

    def toString(self):
        summary  = "spdbcoord"+str(self.longitude)
        summary += " "
        summary += "spdbcoord"+str(self.latitude)
        return summary

###############################################################################

class TweetsPlace:
    """ Place related to the tweet. It doesn't have to be a place of tweet origin.
    The tweet may simply refer to some place.
    Bounding box is defined as geoJSON, therefore for now skipping it.
    """
    def __init__(self, isValid=False, country='', full_name='', place_type='', coordinates=TweetsCoordinates()):
        self.isValid = isValid
        self.country = country.replace(" ", "")       # country full name
        if self.country == "":
            self.country = "undefined"
        self.full_name = full_name.replace(" ", "")   # city and state
        self.place_type = place_type.replace(" ", "") # e.g. city
        if coordinates.isValid == False:
            self.isValid = False
        self.coordinates = coordinates

    def toString(self):
        summary  = "spdbcountryname"+self.country
        summary += " "
        summary += "spdbplacename"+self.full_name
        summary += " "
        summary += "spdbplacetype"+self.place_type
        summary += " "
        #print( "type ", type(self.coordinates.longitude), self.coordinates.longitude )
        summary += self.coordinates.toString()
        return summary

###############################################################################
        
def placeDecoder(obj):
    try:
        obj_iterator = iter(obj)
    except TypeError, te:
        print( obj, 'placeDecoder is not iterable' )
        return TweetsPlace()

    if 'country' and 'full_name' and 'place_type' and 'bounding_box' in obj_iterator:
        return TweetsPlace(True, obj['country'], obj['full_name'], obj['place_type'],
		           TweetsCoordinates(True, obj['bounding_box']))
    else:
        print ('place_decoder fail: missing country, full_name, place_type or bounding_box')
        #print (obj)
        return TweetsPlace()

###############################################################################

class TweetForClustering:
    """This class is meant to represent essential tweet data
    needed for clustering algorithms.
    """   

    def __init__(self, isValid=False, tweetId=0, text='', placeObj=''):
        self.isValid = isValid
        self.tweetId = tweetId
        self.text    = ' '.join(text.split()) # utf-8 text, remove all new line, tab chars
        if isValid == True:
	    try:
	        obj_iterator = iter(placeObj)
	        self.place = placeDecoder(placeObj)
	    except TypeError, te:
		print( 'TweetForClustering: placeObj is not iterable', placeObj )
		self.isValid = False

    def dump(obj):
        for attr in dir(obj):
            print "obj.%s = %s" % (attr, getattr(obj, attr))

    def toString(self):
        summary  = self.text
        summary += " "
        summary += self.place.toString()
        return summary

###############################################################################

def tweetDecoder(obj):
    try:
        obj_iterator = iter(obj)
    except TypeError, te:
        print( obj, 'tweet_decoder is not iterable' )
        return TweetForClustering()
   
    if 'id_str' and 'text' and 'place' in obj_iterator:
        tweet = TweetForClustering(True, obj['id_str'], obj['text'], obj['place'])
        return tweet
    else:
        print ('tweet_decoder fail: missing id_str or text or place')
        #print (obj) #json.dumps(obj, indent=4, sort_keys=False)
        return TweetForClustering()

###############################################################################

def parseData(pathToRawTweets, summaryParsedTweets):
    print( "Parsing raw data..." )
        
    removeFile(summaryParsedTweets)
    summaryfile = open(summaryParsedTweets, 'w')

    for file in os.listdir(pathToRawTweets):
        print( '{0}\r'.format("Parsing: %s" % file) ),
	#print( "Processing object file: %s" % file )
	fullFileName = os.getcwd()+"/"+pathToRawTweets+"/"+file
	fIn = open(fullFileName, 'r')

	try:
	    tweet = tweetDecoder(json.load(fIn))
	except ValueError, ve:
	    print( "Decoding error ", json.dumps(fIn.read()) )
            fIn.close()
            removeFile(fullFileName)
            continue

	if tweet.isValid == False:
	    print("Invalid object file: %s" % file)
	    try:
	        print json.dump(tweet, indent=4, sort_keys=False)
	    except TypeError, te:
	        print( fIn.read() )

            fIn.close()
            removeFile(fullFileName)
            continue

	fIn.close()

	#print( " %s " % tweet.toString() )
	exclude = set(string.punctuation)

        # remove punctuations
	tweetForStem = ''.join(ch for ch in tweet.toString() if ch not in exclude)

        # discard unicode specific characters
        tweetForStemClean = ''.join([i if ord(i) < 128 else ' ' for i in tweetForStem])

        summaryfile.write(file+" "+tweetForStemClean+'\n')

    # go to next line
    print ("Parsed %d items                   " % len(os.listdir(pathToRawTweets)) )
   
    summaryfile.close()

###############################################################################

def stemData(summaryParsedTweets, summaryStemmedTweets):
    print( "Stemming parsed data..." )

    removeFile(summaryStemmedTweets)

    # run C code for stemming
    from ctypes import cdll
    lib = cdll.LoadLibrary('./cmake_stemmer/libstemmer.so')

    ret = lib.stem(summaryParsedTweets, summaryStemmedTweets)
    #print( "stem success: ", ret==0 )

###############################################################################

def tfidfData(summaryStemmedTweets, summaryTfidfTweets, summaryStopWords,
              dictionaryFile, threshold, sampleRatio):
    print( "TFIDFing stemmed data..." )
    removeFile(summaryTfidfTweets)
    removeFile(summaryStopWords)
    removeFile(dictionaryFile)

    fIn = open(summaryStemmedTweets, 'r')
    lineCount = 0
    for line in fIn:
        lineCount = lineCount + 1
    fIn.close()

    stemFileReduced = "summaryStemFileReduced.txt"
    removeFile(stemFileReduced)
    fOut = open(stemFileReduced, 'w')
    outputSetSize = int(lineCount*sampleRatio)
    print( "Desired tweet set size %d" % outputSetSize )
    lineSet = random.sample(range(1,lineCount,1), outputSetSize)
    lineCount = 0
    fIn = open(summaryStemmedTweets, 'r')
    for line in fIn:
        lineCount = lineCount + 1
        if lineCount in lineSet:
            fOut.write(line)

    fOut.close()
    fIn.close()

    summaryStemmedTweets = stemFileReduced

    # run C code for tfidf
    from ctypes import cdll
    lib = cdll.LoadLibrary('./cmake_tfidf/libtfidf.so')

    class TFIDF(object):
	def __init__(self):
	    self.obj = lib.TFIDF_New()

	def preRun(self, stemFileIn, tfidfFileOut, threshold, stopWordFileInOut):
	    lib.TFIDF_CreateStopWordList_Run(self.obj, stemFileIn, tfidfFileOut, threshold, stopWordFileInOut)

	def run(self, stemFileIn, tfidfFileOut, stopWordFileInOut, dictionaryFileOut):
	    lib.TFIDF_UseStopWordList_Run(self.obj, stemFileIn, tfidfFileOut, stopWordFileInOut, dictionaryFileOut)

    tfidf = TFIDF()
    tfidf.preRun(summaryStemmedTweets, summaryTfidfTweets, c_double(threshold), summaryStopWords)

    tfidf = TFIDF()
    tfidf.run(summaryStemmedTweets, summaryTfidfTweets, summaryStopWords, dictionaryFile)
    

    bashCommand = "wc -l summaryTfidfDictionary.txt"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    #bashCommand = "cut -f 1 -d ' '"
    #process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    #output = process.communicate()[0]
    print( "TFIDF resulted features size is %s " % (output) )

###############################################################################

def makeMatrixFile(summaryTfidfTweets, tweetsMatrixFile):
    print( "Making matrix for clustering..." )
    removeFile(tweetsMatrixFile)
    matrixfile = open(tweetsMatrixFile, 'w')

    fIn = open(summaryTfidfTweets, 'r')
    rowIndex = 1
    for line in fIn:
        #skip json name
        line = line.split(' ', 1)[1]

        #split to index:value pairs
        wordCollection = line.split(' ')

        #matrixEntries: each value is given in triple (row coordinate, column coordinate, value)

        currentIndex = 0
        for entry in wordCollection:
            if entry.strip() == '':
                continue
            #print( "entry'%s'" % entry )
            pair = entry.split(':')
            columnIndex = int(pair[0])
            value = float(pair[1])
            matrixfile.write(str(rowIndex)+' '+str(columnIndex)+' '+str(value))
            matrixfile.write('\n')

        rowIndex = rowIndex + 1
    
    matrixfile.close()    

    return

############################################################################### 

