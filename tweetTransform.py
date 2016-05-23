from rpy2.robjects.packages import importr, data
import numpy

import simplejson
import json
import os
import sys

###############################################################################

class TweetsCoordinates:
    COORDS_STEM_PREFIX = "COORDS"
    def __init__(self, isValid=False, obj=''):
        self.isValid = isValid
        if isValid == True:
		if 'coordinates' in obj and \
		    len(obj['coordinates']) == 2 and \
		        'type' in obj and obj['type'] == 'Point':
		    self.longitude = obj['coordinates'][0]
		    self.latitude = obj['coordinates'][1]
		else:
		    self.isValid = False
		    print ('TweetsCoordinates fail: coordinates are wrong')
		    #print (obj)
		    #raise Exception('Invalid object passed to TweetsCoordinates, cannot intialize')
    
    def get_stemmed(self):
        return format('{0}{1}{2}', self.COORDS_STEM_PREFIX, round(longitude), round(latitude))

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
        print (obj)
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
		    print( 'TweetForClustering: placeObj is not iterable %s' % placeObj )
		    self.isValid = False

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
    for root, dirs, files in os.walk(pathToRawTweets, topdown=False):
        for file in files:
            fullFileName = os.path.join(root, file)
            f = open(fullFileName, 'r')
            # TODO how to open the file?
            # option 1
            allLines = f.read()
            tweet = json.loads(allLines, object_hook=tweet_decoder)
            # option 2
            #json.load(f, object_hook=tweet_decoder)

	    if tweet.isValid == False:
                print("Invalid object file: %s" % file)
                try:
                    print json.dumps(allLines, indent=4, sort_keys=False)
                except TypeError, te:
                    print( allLines )
                continue

            outfile = open(fullFileName+"stem", 'w')
#            tweet >> outfile TODO save object as string to file
            outfile.close()

            # run C code for stemming
            from ctypes import cdll
	    lib = cdll.LoadLibrary('./cmake_stemmer/libstemmer.so')

            lib.stem(fullFileName+"stem", pathToStemmedTweets+file)

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
