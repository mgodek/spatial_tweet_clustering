from rpy2.robjects.packages import importr, data
import numpy

import re, string, timeit
import shutil
from pprint import pprint
import simplejson
import json
import os
import sys

###############################################################################

class TweetsCoordinates:
    #COORDS_STEM_PREFIX = "COORDS"
    def __init__(self, isValid=False, obj=''):
        self.isValid = isValid
        if isValid == True:
            if 'coordinates' in obj : # and len(obj['coordinates']) >= 2 :
                coor = obj['coordinates']
                #print( coor[0] )
		self.longitude = coor[0][0][0]
		self.latitude = coor[0][0][1]
            else:
		self.isValid = False
		print ('TweetsCoordinates fail: coordinates are wrong')
		#print (obj)
		#raise Exception('Invalid object passed to TweetsCoordinates, cannot intialize')
    
    def toString(self):
        summary  = str(round(self.longitude))
        summary += " "
        summary += str(round(self.latitude))
        return summary

###############################################################################

class TweetsPlace:
    """ Place related to the tweet. It doesn't have to be a place of tweet origin.
    The tweet may simply refer to some place.
    Bounding box is defined as geoJSON, therefore for now skipping it.
    """
    PLACE_STEM_PREFIX = "PLACE"
    def __init__(self, isValid=False, country='', full_name='', place_type='', coordinates=TweetsCoordinates()):
        self.isValid = isValid
        self.country = country       # country full name
        self.full_name = full_name   # city and state
        self.place_type = place_type # e.g. city
        if coordinates.isValid == False:
            self.isValid = False
        self.coordinates = coordinates

    def toString(self):
        summary  = self.country
        summary += " "
        summary += self.full_name
        summary += " "
        summary += self.place_type
        summary += " "
        #print( "type ", type(self.coordinates.longitude), self.coordinates.longitude )
        summary += self.coordinates.toString()
        return summary

###############################################################################
        
def place_decoder(obj):
    try:
        obj_iterator = iter(obj)
    except TypeError, te:
        print( obj, 'place_decoder is not iterable' )
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
        self.text = text # utf-8 text
        if isValid == True:
	    try:
	        obj_iterator = iter(placeObj)
	        self.place = place_decoder(placeObj)
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

def tweet_decoder(obj):
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

def stemData(pathToRawTweets, pathToStemmedTweets):
    print( "Stem data in all files" )
    shutil.rmtree( "tweetsTemp" )
    os.mkdir("tweetsTemp")
        
    for file in os.listdir(pathToRawTweets):
	    print( '{0}\r'.format("Processing object file: %s" % file) ),
	    #print( "Processing object file: %s" % file )
	    fullFileName = os.getcwd()+"/"+pathToRawTweets+"/"+file #os.path.join(root, file)
	    f = open(fullFileName, 'r')
	    
	    # TODO how to open the file?
	    # option 1
	    #allLines = f.read()
	    #tweet = json.loads(allLines, object_hook=tweet_decoder)
	    # option 2
	    try:
		tweet = tweet_decoder(json.load(f))#, object_hook=tweet_decoder)
	    except ValueError, ve:
		print( "Decoding error ", json.dumps(f.read()) )
		continue

	    if tweet.isValid == False:
		print("Invalid object file: %s" % file)
		try:
		    #print json.dumps(allLines, indent=4, sort_keys=False)
		    print json.dump(tweet, indent=4, sort_keys=False)
		except TypeError, te:
		    #print( allLines )
		    print( f.read() )
		    f.close()
		continue
	    f.close()

	    #print("Stemming object file: %s" % file)
	    fileForStem = fullFileName.replace( "tweets", "tweetsTemp" )
	    #print( "temp %s" % fileForStem )
	    outfile = open(fileForStem, 'w')
	    #print( " %s " % tweet.toString() )
	    exclude = set(string.punctuation)
	    tweetForStem = ''.join(ch for ch in tweet.toString() if ch not in exclude) # remove punctuations
	    #print( "tweetForStem: %s" % tweetForStem ) 
	    outfile.write(''.join([i if ord(i) < 128 else ' ' for i in tweetForStem])) # discard unicode specific characters
	    #print( " %s " % tweetForStem )
	    outfile.close()

	    # run C code for stemming
	    from ctypes import cdll
	    lib = cdll.LoadLibrary('./cmake_stemmer/libstemmer.so')

	    ret = lib.stem(fileForStem, pathToStemmedTweets+"/"+file)
	    #print( "stem ret ", ret )

    print # go to next line

###############################################################################

def tfidfData(pathToStemmedTweets):
    print( "TFIDF data in all files" )
    for root, dirs, files in os.walk(pathToStemmedTweets, topdown=False):
        for file in files:
            fullFileName = os.path.join(root, file)

	    # run C code for tfidf
	    from ctypes import cdll
	    lib = cdll.LoadLibrary('./cmake_tfidf/libtfidf.so')

	    class TFIDF(object):
		def __init__(self):
		    self.obj = lib.TFIDF_New()

		def parse(self, fullFileName):
		    lib.TFIDF_Run(self.obj, fullFileName)

	    tfidf = TFIDF()
	    tfidf.parse(fullFileName) 

###############################################################################

def makeMatrixFiles(pathToStemmedTweets, tweetsMatrixFile, tweetsFeatureListFile):
    print( "TODO generate files being a matrix representation -> tweetsMatrixFile (matrixEntries: each row is a tweet, each column is a feature, featureListing: each row is a word-feature mapping to column features in matrixEntries -> tweetsFeatureListFile) of all files" ) #TODO
    return 
