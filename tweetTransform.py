from rpy2.robjects.packages import importr, data
import ctypes
import numpy

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
        if 'coordinates' in obj and \
            len(obj['coordinates']) == 2 and \
                'type' in obj and obj['type'] == 'Point':
            self.longitude = obj['coordinates'][0]
            self.latitude = obj['coordinates'][1]
        else:
            self.isValid = False
            logging.debug('TweetsCoordinates fail')
            #print (obj)
            #raise Exception('Invalid object passed to TweetsCoordinates, cannot intialize')
    
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
    def __init__(self, isValid=False, country='', full_name='', name='', place_type='', coordinates=TweetsCoordinates()):
        self.isValid = isValid
        self.country = country       # country full name
        self.full_name = full_name   # city and state
        self.name = name             # city name
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

    if 'country' and 'full_name' and 'name' and 'place_type' and 'coordinates' in obj_iterator:
	    return TweetsPlace(True, obj['country'], obj['full_name'],
		               obj['name'], obj['place_type'],
		               TweetsCoordinates(True, obj['coordinates']))
    else:
        logging.debug ('place_decoder fail')
        logging.debug (obj)
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
            if not isinstance(placeObj, dict):
                raise TypeError
            self.place = place_decoder(placeObj['place'])
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
   
    if 'id_str' and 'lang' and 'text' and 'place' in obj:
        tweet = TweetForClustering(True, obj['id_str'], obj['lang'], obj['text'], obj)
        return tweet
    else:
        logging.debug ('tweet_decoder fail')
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
            fullFileName = os.path.join(root, file)
            f = open(fullFileName, 'r')
            for line in f:
                tweet = json.loads(line, object_hook=tweet_decoder)

	    if tweet.isValid == False:
                logging.debug("Invalid object file: %s" % file)
                try:
                    logging.debug json.dumps(line, indent=4, sort_keys=False)
                except TypeError, te:
                    logging.debug( line )
                continue
            stemmedData = tweet.get_stemmed(doStemming, stemmer_p)
            results.append({'id' : tweet.id, 'data': stemmedData})
	    
            #TODO put tweet to stem instead of what is under fullFileName
            
            lib.stem(fullFileName, pathToStemmedTweets+file)
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
