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
        if 'coordinates' in obj and \
            len(obj['coordinates']) == 2 and \
                'type' in obj and obj['type'] == 'Point':
            self.longitude = obj['coordinates'][0]
            self.latitude = obj['coordinates'][1]
        else:
            self.isValid = False
            print ('TweetsCoordinates fail')
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
    def __init__(self, isValid=False, country='', full_name='', name='', place_type='', coordinates=TweetsCoordinates()):
        self.isValid = isValid
        self.country = country       # country full name
        self.full_name = full_name   # city and state
        self.name = name             # city name
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

    if 'country' and 'full_name' and 'name' and 'place_type' and 'coordinates' in obj_iterator:
	    return TweetsPlace(True, obj['country'], obj['full_name'],
		               obj['name'], obj['place_type'],
		               TweetsCoordinates(True, obj['coordinates']))
    else:
        print ('place_decoder fail')
        print (obj)
        return TweetsPlace()

###############################################################################

class TweetForClustering:
    """This class is meant to represent essential tweet data
    needed for clustering algorithms.
    """   

    def __init__(self, isValid=False, tweetId=0, coordinates=[], lang='NA', text='', placeObj=''):
        self.isValid = isValid
        self.tweetId = tweetId
        self.coords = coordinates
        self.lang = lang # language code
        self.text = text # utf-8 text
        try:
            obj_iterator = iter(placeObj)
            self.place = place_decoder(placeObj['place'])
        except TypeError, te:
            print( placeObj, 'TweetForClustering is not iterable' )
            self.isValid = False

###############################################################################

def tweet_decoder(obj):
    try:
        obj_iterator = iter(obj)
    except TypeError, te:
        print( obj, 'tweet_decoder is not iterable' )
        return TweetForClustering()
   
    if 'id_str' and 'lang' and 'text' and 'place' in obj_iterator:
        tweet = TweetForClustering(True, obj['id_str'], obj['lang'], obj['text'], obj)
        return tweet
    else:
        print ('tweet_decoder fail')
        #print (obj) #json.dumps(obj, indent=4, sort_keys=False)
        return TweetForClustering()

###############################################################################

def stemData(pathToRawTweets, pathToStemmedTweets):
    print( "Stem data in all files" )
    for root, dirs, files in os.walk(pathToRawTweets, topdown=False):
        for file in files:
            fullFileName = os.path.join(root, file)
            f = open(fullFileName, 'r')
            allLines = f.read()#.replace('\n', ' ') # TODO
            tweet = json.loads(allLines, object_hook=tweet_decoder)

	    if tweet.isValid == False:
                print("Invalid object file: %s" % file)
                try:
                    print json.dumps(allLines, indent=4, sort_keys=False)
                except TypeError, te:
                    print( allLines )
                continue

            # run C code for stemming
            from ctypes import cdll
	    lib = cdll.LoadLibrary('./cmake_stemmer/libstemmer.so')
            lib.stem(fullFileName, pathToStemmedTweets+file)

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
