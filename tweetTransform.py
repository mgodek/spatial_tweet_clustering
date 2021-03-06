
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
		self.longitude = int(round(coor[0][0][0])) + 180
		self.latitude = int(round(coor[0][0][1]))  + 90
            else:
		self.isValid = False
		print ('TweetsCoordinates fail: coordinates are wrong')
		#print (obj)
		#raise Exception('Invalid object passed to TweetsCoordinates, cannot intialize')

    def toString(self, addSpdbPrefix):
        if addSpdbPrefix == True:
            summary  = "spdbcoordlong"+str(self.longitude)
        else:
            summary  = str(self.longitude)
        summary += " "

        if addSpdbPrefix == True:
            summary += "spdbcoordlat"+str(self.latitude)
        else:
            summary += str(self.latitude)
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

    def toString(self, addSpdbPrefix):
        if addSpdbPrefix == True:
            summary  = "spdbcountryname"+self.country
        else:
            summary  = self.country
        summary += " "

        if addSpdbPrefix == True:
            summary += "spdbplacename"+self.full_name
        else:
            summary += self.full_name
        summary += " "

        if addSpdbPrefix == True:
            summary += "spdbplacetype"+self.place_type
        else:
            summary += self.place_type
        summary += " "
        #print( "type ", type(self.coordinates.longitude), self.coordinates.longitude )
        summary += self.coordinates.toString(addSpdbPrefix)
        return summary

###############################################################################
        
def placeDecoder(obj):
    try:
        obj_iterator = iter(obj)
    except TypeError, te:
        #print( obj, 'placeDecoder is not iterable' )
        return TweetsPlace()

    if 'country' and 'full_name' and 'place_type' and 'bounding_box' in obj_iterator:
        return TweetsPlace(True, obj['country'], obj['full_name'], obj['place_type'],
		           TweetsCoordinates(True, obj['bounding_box']))
    else:
        print ('place_decoder fail: missing country, full_name, place_type or bounding_box')
        return TweetsPlace()

###############################################################################

class TweetForClustering:
    """This class is meant to represent essential tweet data
    needed for clustering algorithms.
    """   

    def __init__(self, isValid=False, tweetId=0, text='', placeObj='', userObj=''):
        self.isValid = isValid
        self.tweetId = tweetId
        self.text    = ' '.join(text.split()) # utf-8 text, remove all new line, tab chars
        if self.isValid == True:
            self.place = placeDecoder(placeObj)	    
            if self.place.isValid == False:
                self.isValid = False
                #print( 'TweetForClustering: placeObj is not valid' )

            if len(self.text) < 40: # TODO maybe should have other value
                self.isValid = False
                #print( 'TweetForClustering: text is too short %d < %d' % (len(self.text), 50) )

            # decode userObj
            try:
                obj_iterator = iter(userObj)
                self.userLocation = ' '.join(str(userObj['location']).replace(" ", "").split())
            except:
                self.isValid = False
                #print( 'userObj is not iterable' )
                return

    def dump(obj):
        for attr in dir(obj):
            print "obj.%s = %s" % (attr, getattr(obj, attr))

    def toString(self, addSpdbPrefix):
        summary  = self.text
        summary += " "
        if addSpdbPrefix == True:
            summary += "spdbuserlocation"+self.userLocation
        else:
            summary += self.userLocation
        summary += " "
        summary += self.place.toString(addSpdbPrefix)
        return summary

###############################################################################

def tweetDecoder(obj):
    try:
        obj_iterator = iter(obj)
    except TypeError, te:
        print( obj, 'tweet_decoder is not iterable' )
        return TweetForClustering()
   
    try:
        if 'id_str' and 'text' and 'place' and 'user' in obj_iterator:
            tweet = TweetForClustering(True, obj['id_str'], obj['text'], obj['place'], obj['user'])
            if tweet.isValid == True:
                return tweet
    except KeyError, ke:
        print ('tweet_decoder fail: missing id_str or text or place or user')
        #print (obj) #json.dumps(obj, indent=4, sort_keys=False)

    return TweetForClustering()

###############################################################################

def parseData(onlySpdbData, summaryRawTweets, parsedTweetsFileName, addSpdbPrefix):
    print( "Parsing raw data..." )
        
    removeFile(parsedTweetsFileName)
    summaryfile = open(parsedTweetsFileName, 'w')

    fIn = open(summaryRawTweets, 'r')

    tweetCountAll = 0
    tweetCountCorrect = 0
    tweetCollection = fIn.read().splitlines()
    for tweetString in tweetCollection:
        tweetCountAll += 1
        print( '{0}\r'.format("Parsing: %d" % tweetCountAll) ),

        tweet = json.loads(tweetString)

	try:
	    tweetDecoded = tweetDecoder(tweet)
	except ValueError, ve:
	    print( "Decoding error ", json.dumps(tweet) )
            continue

	if tweetDecoded.isValid == False:
	    #print("Invalid object file: %d" % tweetCountAll)
	    try:
	        print json.dump(tweet, indent=4, sort_keys=False)
	    except TypeError, te:
	        #print( tweet )
                continue

            continue

        tweetCountCorrect += 1

	#print( " %s " % tweet.toString() )
	exclude = set(string.punctuation)

        # remove punctuations
	tweetForStem = ''.join(ch for ch in tweetDecoded.toString(addSpdbPrefix) if ch not in exclude)

        # discard unicode specific characters
        tweetForStemClean = ''.join([i if ord(i) < 128 else ' ' for i in tweetForStem])

        if onlySpdbData == True:
            tweetForStemClean = ' '.join(word for word in tweetForStemClean.split(' ') if word.startswith('spdb'))

        summaryfile.write(str(tweetDecoded.tweetId)+" "+tweetForStemClean+'\n')

    fIn.close()

    # go to next line
    print ("Parsed %d items with %d correct tweets." % (tweetCountAll, tweetCountCorrect) )

    summaryfile.close()
    print("Parsed result saved to '%s'" % parsedTweetsFileName )

###############################################################################

def stemData(summaryParsedTweets, stemmedTweetsFileName):
    print( "Stemming parsed data..." )

    removeFile(stemmedTweetsFileName)

    # run C code for stemming
    from ctypes import cdll
    lib = cdll.LoadLibrary('./cmake_stemmer/libstemmer.so')

    ret = lib.stem(summaryParsedTweets, stemmedTweetsFileName)
    #print( "stem success: ", ret==0 )
    print("Stemmed result saved to '%s'" % stemmedTweetsFileName )

###############################################################################

def tfidfData(stemmedTweetsFileName, summaryTfidfTweets, summaryStopWords, dictionaryFile,
              featureFileOut, thresholdUpper, thresholdBottom, stopWordCountBottom):
    print( "TFIDFing stemmed data..." )
    removeFile(summaryTfidfTweets)
    removeFile(summaryStopWords)
    removeFile(dictionaryFile)
    removeFile(featureFileOut)

    fIn = open(stemmedTweetsFileName, 'r')
    lineCount = 0
    for line in fIn:
        lineCount = lineCount + 1
    fIn.close()

    # run C code for tfidf
    from ctypes import cdll
    lib = cdll.LoadLibrary('./cmake_tfidf/libtfidf.so')

    class TFIDF(object):
	def __init__(self):
	    self.obj = lib.TFIDF_New()

	def preRun(self, stemFileIn, tfidfFileOut, thresholdUpper, thresholdBottom, stopWordCountBottom, stopWordFileInOut):
	    lib.TFIDF_CreateStopWordList_Run(self.obj, stemFileIn, tfidfFileOut, thresholdUpper, thresholdBottom, stopWordCountBottom, stopWordFileInOut)

	def run(self, stemFileIn, tfidfFileOut, stopWordFileInOut, dictionaryFileOut, featureFileOut):
	    lib.TFIDF_UseStopWordList_Run(self.obj, stemFileIn, tfidfFileOut, stopWordFileInOut, dictionaryFileOut, featureFileOut)

    tfidf = TFIDF()
    tfidf.preRun(stemmedTweetsFileName, summaryTfidfTweets, c_double(thresholdUpper), c_double(thresholdBottom), c_uint(stopWordCountBottom), summaryStopWords)

    tfidf = TFIDF()
    tfidf.run(stemmedTweetsFileName, summaryTfidfTweets, summaryStopWords, dictionaryFile, featureFileOut)

    bashCommand = "wc -l "+dictionaryFile
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print( "TFIDF resulted features size is %s " % (output) )
    print( "Results saved to %s %s %s %s" % (summaryTfidfTweets, featureFileOut, summaryStopWords, dictionaryFile) )

###############################################################################

def makeClusterMatrixFile(summaryData, tweetsMatrixFile):
    print( "Making matrix for clustering..." )
    removeFile(tweetsMatrixFile)
    matrixfile = open(tweetsMatrixFile, 'w')

    fIn = open(summaryData, 'r')
    rowIndex = 1
    for line in fIn:
        #skip json name
        line = line.split(' ', 1)[1]

        #split to index:value pairs
        featureCollection = line.split(' ')

        #matrixEntries: each value is given in quadriple (row coordinate, column coordinate, value)

        dataLine = ""
        for i in range(0, len(featureCollection)):
            featureStr = ' '.join(str(featureCollection[i]).split())
            dataLine = dataLine + str(rowIndex) + " " + str(i+1) + " " + featureStr +'\n'

        matrixfile.write(dataLine)

        rowIndex = rowIndex + 1
    
    fIn.close()
    matrixfile.close()    

    return

###############################################################################

def extractCoord(dataParsedTweetsFilename, dataParsedCoordFilename):
    print( "Extracting coordinate data... %s" % dataParsedTweetsFilename )
    removeFile(dataParsedCoordFilename)

    fOut = open(dataParsedCoordFilename, 'w')
    fIn = open(dataParsedTweetsFilename, 'r')

    for line in fIn:
        #get json name
        id_str_json = line.split(' ', 1)[0]
        #print( "id_str_json=%s line=%s" % (id_str_json,line) )

        coordStart = line.find('spdbcoordlong') + len('spdbcoordlong') # useing value from Tweet class
        coordEnd = line.find(' ', coordStart)
        longitude = int(line[coordStart:coordEnd])-180

        coordStart = line.find('spdbcoordlat') + len('spdbcoordlat') #using value from Tweet class
        coordEnd = line.find(' ', coordStart)
        latitude = int(line[coordStart:coordEnd])-90
        #print( "id_str_json=%s longitude=%d latitude=%d" % (id_str_json,longitude,latitude) )

        fOut.write(id_str_json+' '+str(latitude)+' '+str(longitude)+'\n')

    fIn.close()
    fOut.close()

############################################################################### 
