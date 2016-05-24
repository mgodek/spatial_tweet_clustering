from rpy2.robjects.packages import importr, data
import ctypes
import numpy

import shutil
from pprint import pprint
import simplejson
import json
import os
import sys
import logging

###############################################################################

class TweetsCoordinates:
    COORDS_STEM_PREFIX = "COORDS"
    def __init__(self, isValid=False, obj=''):
        self.isValid = isValid
        if isValid == True:
            if 'coordinates' in obj : # and len(obj['coordinates']) >= 2 :
                coor = obj['coordinates']
                self.longitude = coor[0][0]
                self.latitude = coor[0][1]
            else:
                self.isValid = False
                print ('TweetsCoordinates fail: coordinates are wrong')
    
    def get_stemmed(self):
        return [format('{0}_{1}', self.COORDS_STEM_PREFIX, round(longitude)),\
            format('{0}_{1}', self.COORDS_STEM_PREFIX, round(latitude))]

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
        
    def get_stemmed(self, stemFunc, stemmer):
        return [str(stemFunc(stemmer, self.country, len(self.country))), \
            str(stemFunc(stemmer, self.full_name, len(self.full_name))), \
                str(stemFunc(stemmer, self.name, len(name))), \
                    str(stemFunc(stemmer, self.place_type, len(self.place_type)))]

###############################################################################
        
def place_decoder(obj):
    try:
        if not isinstance(obj, dict):
            raise TypeError
    except TypeError, te:
        logging.debug( 'argument obj passed to place_decoder is not dict: %s' % str(obj))
        logging.debug('arguemnt type is %s instead' % type(obj))
        return TweetsPlace()

    if 'country' and 'full_name' and 'place_type' and 'bounding_box' in obj_iterator:
        return TweetsPlace(True, obj['country'], obj['full_name'], obj['place_type'],
		           TweetsCoordinates(True, obj['bounding_box']))
    else:
        logging.debug ('place_decoder fail')
        logging.debug (obj)
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
            logging.debug('Argument passed to TweetForClustering is not dict: %s' % str(placeObj))
            logging.debug('arguemnt type is %s instead' % type(placeObj))
		self.isValid = False
            
    def get_stemmed(self, stemFunc, stemmer):
        results = self.place.get_stemmed(stemFunc, stemmer)
        results = results + self.coordinates.get_stemmed()
        for word in self.text.split(" "):
            results.append(str(stemFunc(stemmer, word, len(word))))
            
    

###############################################################################

def tweet_decoder(obj):
    try:
        if not isinstance(obj, dict):
            raise TypeError
    except TypeError, te:
        logging.debug(str(obj)
        logging.debug('argument obj passed to tweet_decoder is not dict' )
        log('arguemnt type is %s instead' % type(obj))
        logging.debug TweetForClustering()
   
    if 'id_str' and 'text' and 'place' in obj_iterator:
        tweet = TweetForClustering(True, obj['id_str'], obj['text'], obj['place'])
        return tweet
    else:
        print ('tweet_decoder fail: missing id_str or text or place')
        #print (obj) #json.dumps(obj, indent=4, sort_keys=False)
        return TweetForClustering()

###############################################################################

def storeStemmedData(path, stemmedData):
    f = open(path, 'w')
    for elem in stemmedData:
        f.write(format("{0}: ", elem['id']))
        for stem in elem['data']:
            f.write(format("{0}, ", stem))
        f.write("\n")
    f.close()
    logging.debug( "Storing done" )

###############################################################################

def stemData(pathToRawTweets, pathToStemmedTweets, logFile):
    results = []
    logging.basicConfig(filename='stemming.log', level=logging.DEBUG)
    logging.debug( "Stem data in all files" )
    logging.debug( "Creating stemmer" )
    shutil.rmtree( "tweetsTemp" )
    os.mkdir("tweetsTemp")
    # C code to get stemming related functions, and assign proper return types 
    lib = ctypes.cdll.LoadLibrary('/home/zby/projects/spdb/spatial_tweet_clustering/libstemmer_c/libstemmer.so')
    createStemmer = lib.sb_stemmer_new
    createStemmer.restype = ctypes.c_void_p
    deleteStemmer = lib.sb_stemmer_delete
    doStemming = lib.sb_stemmer_stem
    doStemming.restype = ctypes.c_char_p
    stemmer_p = createStemmer("en", "UTF_8")
    logging.debug( "Crawling and stemming files" )
    for root, dirs, files in os.walk(pathToRawTweets, topdown=False):
        for file in files:
            print("Filtering object file: %s" % file)
            fullFileName = os.path.join(root, file)
            f = open(fullFileName, 'r')
            try:
                tweet = tweet_decoder(json.load(f))#, object_hook=tweet_decoder)
            except ValueError, ve:
                print( "Decoding error ", json.dumps(f.read()) )
                continue
            if tweet.isValid == False:
                logging.debug("Invalid object file: %s" % file)
                try:

                    logging.debug( json.dump(tweet, indent=4, sort_keys=False))
                    except TypeError, te:
		    logging.debug( json.load(f) )
                continue
            stemmedData = tweet.get_stemmed(doStemming, stemmer_p)
            results.append({'id' : tweet.id, 'data': stemmedData})
	    
            print("Stemming object file: %s" % file)
            readyForStem = fullFileName.replace( "/tweets/", "/tweetsTemp/" )
            outfile = open(readyForStem, 'w')
            #tweet >> outfile TODO save object as string to file
            outfile.close()


            lib.stem(readyForStem, pathToStemmedTweets+file)
            f.close()
    deleteStemmer(stemmer_p)
    logging.debug ( "removed stemmer, storing stuff to %s" %pathToStemmedTweets)
    storeStemmedData(pathToStemmedTweets, results)

###############################################################################

def tfidfData(pathToStemmedTweets):
    print( "TFIDF data in all files" )
    for root, dirs, files in os.walk(pathToStemmedTweets, topdown=False):
        for file in files:
            fullFileName = os.path.join(root, file)

	    # run C code for tfidf
	    from ctypes import cdll
	    lib = ctypes.LoadLibrary('./cmake_tfidf/libtfidf.so')

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
