from rpy2.robjects.packages import importr, data
import numpy

import simplejson
import json
import os
import sys

class TweetsCoordinates:
    COORDS_STEM_PREFIX = "COORDS"
    def __init__(self, obj):
        if 'coordinates' in obj and \
            len(obj['coordinates']) == 2 and \
                'type' in obj and obj['type'] == 'Point':
            self.longitude = obj['coordinates'][0]
            self.latitude = obj['coordinates'][1]
        else:
            raise Exception('Invalid object passed to TweetsCoordinates, cannot intialize')
    
    def get_stemmed(self):
        return format('{0}{1}{2}', self.COORDS_STEM_PREFIX, round(longitude), round(latitude))

class TweetsPlace:
    """ Place related to the tweet. It doesn't have to be a place of tweet origin.
    The tweet may simply refer to some place.
    Bounding box is defined as geoJSON, therefore for now skipping it.
    """
    PLACE_STEM_PREFIX = "PLACE"
    def __init__(self, country, full_name, name, place_type):
        self.country = country #country full name
        self.full_name = full_name # city and state
        self.name = name #city
        self.place_type = place_type # e.g. city
        
def place_decoder(obj):
    return TweetsPlace(obj['country'], obj['full_name'], obj['name'], obj['place_type'])


class TweetForClustering:
    """This class is meant to represent essential tweet data
    needed for clustering algorithms.
    """
    
    def __init__(self, id, coordinates, lang, text, place):
        self.initialized = True
        self.coords = coordinates
        self.id = id
        self.lang = lang # language code
        self.text = text #utf-8 text
        
def tweet_decoder(obj):
    tweet = TweetForClustering(
        obj['id'],
        TweetsCoordinates(obj['coordinates']),
        obj['lang'],
        obj['text'],
        place_decoder(obj['place']))
    tweet.coords = obj['coordinates']
    return tweet

def stemData(pathToRawTweets, pathToStemmedTweets):
    print( "Prepare data in all files" )
    for root, dirs, files in os.walk(pathToRawTweets, topdown=False):
        for file in files:
            f = open(os.path.join(root, file), 'r')
            allLines = ''
            for line in f:
                allLines = '{0}{1}'.format(allLines,line)
            #tweet = json.loads(allLines, object_hook=tweet_decoder) #TODO this line fails?
            print( "TODO stemming of text and place here" ) #TODO pathToStemmedTweets

            # run C code for stemming
            print( "Stem file" )
            from ctypes import cdll
	    lib = cdll.LoadLibrary('./cmake_stemmer/libstemmer.so')
            lib.stem("fileIn", "fileOut") #TODO maybe just pass filename to parser?

            # run C code for tfidf
            print( "TFIDF file" )
            from ctypes import cdll
	    lib = cdll.LoadLibrary('./cmake_tfidf/libtfidf.so')

	    class TFIDF(object):
	        def __init__(self):
		    self.obj = lib.TFIDF_New()

	        def parse(self):
		    lib.TFIDF_Run(self.obj)

	    tfidf = TFIDF()
            tfidf.parse() #TODO maybe just pass filename to parser?
            #yield tweet

def makeMatrixFiles(pathToStemmedTweets, tweetsMatrixFile, tweetsFeatureListFile):
    print( "TODO generate files being a matrix representation -> tweetsMatrixFile (matrixEntries: each row is a tweet, each column is a feature, featureListing: each row is a word-feature mapping to column features in matrixEntries -> tweetsFeatureListFile) of all files" ) #TODO
    return 
