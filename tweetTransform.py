from rpy2.robjects.packages import importr, data
import ctypes
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
    COORDS_STEM_PREFIX = "COORDS"
    def __init__(self, isValid=False, obj=''):
        self.isValid = isValid
        if isValid == True:
            if 'coordinates' in obj : # and len(obj['coordinates']) >= 2 :
                coor = obj['coordinates']
                self.longitude = float(coor[0][0][0])
                self.latitude = float(coor[0][0][1])
            else:
                self.isValid = False
                print ('TweetsCoordinates fail: coordinates are wrong')
    
    def get_stemmed(self):
        if self.isValid:
            return ["%s_%s"%(self.COORDS_STEM_PREFIX, str(round(self.longitude))),\
                "%s_%s"%(self.COORDS_STEM_PREFIX, str(round(self.latitude)))]
        else:
            return []
    
    def toString(self):
        if self.isValid:
            summary  = str(round(self.longitude))
            summary += " "
            summary += str(round(self.latitude))
            return summary
        else:
            return ''

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
        #print self.country
         
    def get_stemmed(self, stemFunc, stemmer):
        if self.isValid:
            return [str(stemFunc(stemmer, self.country, len(self.country))), \
                str(stemFunc(stemmer, self.full_name, len(self.full_name))), \
                    str(stemFunc(stemmer, self.place_type, len(self.place_type)))] + self.coordinates.get_stemmed()
        else:
            return []
    
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
       if not isinstance(obj, dict):
           raise TypeError
    except TypeError, te:
        print( 'argument obj passed to place_decoder is not dict: %s' % str(obj))
        print('arguemnt type is %s instead' % type(obj))
        return TweetsPlace()

    if 'country' and 'full_name' and 'place_type' and 'bounding_box' in obj:
        return TweetsPlace(True, obj['country'], obj['full_name'], obj['place_type'],
                   TweetsCoordinates(True, obj['bounding_box']))
    else:
        print ('place_decoder fail')
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
                self.place = place_decoder(placeObj)
            except TypeError, te:
                print('Argument passed to TweetForClustering is not dict: %s' % str(placeObj))
                print('arguemnt type is %s instead' % type(placeObj))
                self.isValid = Falseself.isValid = False
     
    def get_stemmed(self, stemFunc, stemmer):
        results = self.place.get_stemmed(stemFunc, stemmer)
        for word in self.text.split(" "):
            results.append(str(stemFunc(stemmer, word, len(word))))
        return results
    
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
        print(str(obj))
        print('argument obj passed to tweet_decoder is not dict' )
        print('arguemnt type is %s instead' % type(obj))
        return TweetForClustering()
   
    if 'id_str' and 'text' and 'place' in obj_iterator:
        tweet = TweetForClustering(True, obj['id_str'], obj['text'], obj['place'])
        return tweet
    else:
        print ('tweet_decoder fail: missing id_str or text or place')
        #print (obj) #json.dumps(obj, indent=4, sort_keys=False)
        return TweetForClustering()

###############################################################################

class StemmingResult:
    
    def __init__(self, tweetId, data):
        self.tweetId = tweetId
        self.listOfStems = data

def storeStemmedData(path, stemmedData):
    try:
        with open(path, 'w') as stemmedFile:
            if stemmedData == None or len(stemmedData) == 0:
                print('Empty results while storing')
                raise ValueError
            for elem in stemmedData:
                stemmedFile.write(str(elem.tweetId))
                stemmedFile.write(':')
                if elem.listOfStems == None or len(elem.listOfStems) == 0:
                    print('Empty data for tweet')
                    continue
                for stem in elem.listOfStems:
                    stemmedFile.write(stem)
                    stemmedFile.write(',')
                stemmedFile.write("\n")
            stemmedFile.flush()
        print( "Storing done" )
    except IOError as e:
        print "Storing Stems Failure: I/O error({0}): {1}".format(e.errno, e.strerror)

###############################################################################

def stemData(pathToRawTweets, pathToStemmedTweets):
    results = []
    #logging.basicConfig(filename='stemming.log', level=print)
    print( "Stem data in all files" )
    print( "Creating stemmer" )
    lib = ctypes.cdll.LoadLibrary('/home/zby/projects/spdb/spatial_tweet_clustering/libstemmer_c/libstemmer.so')
    createStemmer = lib.sb_stemmer_new
    createStemmer.restype = ctypes.c_void_p
    deleteStemmer = lib.sb_stemmer_delete
    doStemming = lib.sb_stemmer_stem
    doStemming.restype = ctypes.c_char_p
    stemmer_p = createStemmer("en", "UTF_8")
    print( "Crawling and stemming files" )
    logs = open('stemming.log', 'w')
    validTweets = 0
    invalidTweets = 0
    for file in os.listdir(pathToRawTweets):
        fullFileName = os.getcwd()+"/"+pathToRawTweets+"/"+file #os.path.join(root, file)
        f = open(fullFileName, 'r')
        try:
            tweet = tweet_decoder(json.load(f))#, object_hook=tweet_decoder)
        except ValueError, ve:
            logs.write( "Decoding error %s \n" % json.dumps(f.read()))
            f.close()
            continue
        if tweet.isValid == False:
            logs.write("Invalid object file: %s \n" % file)
            invalidTweets += 1
            f.close()
            continue
        else:
            validTweets += 1
            stemmedData = tweet.get_stemmed(doStemming, stemmer_p)
            logs.write("stemmed data len is %d"% len(stemmedData))
            results.append(StemmingResult(tweet.tweetId, stemmedData))
        f.close()
        logs.flush()
    logs.write("\n\n VALID: %d"% validTweets)
    logs.write("\n\n INVALID: %d"% invalidTweets)
    print("Storing stuff to %s" %pathToStemmedTweets)
    storeStemmedData(pathToStemmedTweets, results)
    print('Deleting stemmer')
    deleteStemmer(stemmer_p)
    print('Removed stemmer')
    logs.close()
    #logging.flush()

############################################################################################

def stemData_CONFLICT(pathToRawTweets, pathToStemmedTweets):
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
            f.close()
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

###############################################################################

def tfidfData(pathToStemmedTweets):
    print( "TFIDF data in all files" )
    stemmedFile = open(pathToStemmedTweets, 'r')
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
