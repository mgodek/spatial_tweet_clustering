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
from datetime import datetime


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

def getStemmedWords(text, words):
    res = []
    for w in text.split():
        if w in words:
            res.append(words[w])
    return res

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
         
    def get_stemmed(self, words):
        if self.isValid:
            return getStemmedWords(self.country, words) + getStemmedWords(self.full_name, words) + getStemmedWords(self.place_type, words) + self.coordinates.get_stemmed()
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
     
    def get_stemmed(self, words):
        results = self.place.get_stemmed(words)
        for word in self.text.split():
            results.append(words[word])
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

def storeStemmedData(path, stemmedData, logs):
    try:
        with open(path, 'w') as stemmedFile:
            if stemmedData == None or len(stemmedData) == 0:
                logs.write('Empty results while storing\n')
            for elem in stemmedData:
                stemmedFile.write(str(elem.tweetId))
                stemmedFile.write(':')
                if elem.listOfStems == None or len(elem.listOfStems) == 0:
                    logs.write('Empty data for tweet\n')
                    continue
                for stem in elem.listOfStems:
                    stemmedFile.write(stem)
                    stemmedFile.write(',')
                stemmedFile.write("\n")
            stemmedFile.flush()
        logs.write( "Storing done\n" )
    except IOError as e:
        logs.write("Storing Stems Failure: I/O error({0}): {1}\n".format(e.errno, e.strerror))

###############################################################################

class PreparationResult:
    def __init__(self, words={}, tweets=[]):
        self.tweets = tweets
        self.words = words

def writeWordsFromTextToFile(text, outfile, words):
    for w in text.split():
        if w not in words:
            words[w] = ''
            outfile.write("%s\n"%w)
        

def prepareDataForStemming(pathToRawTweets, pathToPreStemmedTweets):
    print( "storing words from tweets" )
    logs = open('stemming.log', 'a')
    logs.write("%s @ prepareDataForStemming METHOD"%datetime.now().strftime('%Y%m%d_%H:%M:%S - '))
    validTweets = 0
    invalidTweets = 0
    preStemming = open(pathToPreStemmedTweets, 'w')
    tweets = []
    words = {}
    logs.write("readgin tweets from %s\n"%pathToRawTweets)
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
            tweets.append(tweet)
        f.close()
        logs.flush()
    logs.write("writing words to stem to %s file\n"%pathToPreStemmedTweets)
    logs.write("\n\n VALID: %d\n"% validTweets)
    logs.write("\n\n INVALID: %d\n"% invalidTweets)
    for t in tweets:
        writeWordsFromTextToFile(t.text, preStemming, words)
        writeWordsFromTextToFile(t.place.country, preStemming, words)
        writeWordsFromTextToFile(t.place.full_name, preStemming, words)
        writeWordsFromTextToFile(t.place.place_type, preStemming, words)
    preStemming.flush()
    logs.close()
    preStemming.close()
    return PreparationResult(words, tweets)

##############################################################################################

def stemData(pathToPreparedStemms, pathToStemmedTweets, prepResults):
    results = []
    #logging.basicConfig(filename='stemming.log', level=print)
    print( "Stem data in all files" )
    
    logs = open('stemming.log', 'a')
    logs.write("%s @ stemData METHOD\n"%datetime.now().strftime('%Y%m%d_%H:%M:%S - '))
    stems = open(pathToPreparedStemms, 'r')
    logs.write("reading stems from %s file\n"%pathToPreparedStemms)
    for line in stems:
        items = line.split()
        if len(items) == 1:
            prepResults.words[items[0]] = items[0]
            continue
        if len(items) != 2:
            logs.write("Error while reading stems: %s\n"% line)
            continue
        prepResults.words[items[0]] = items[1]
    logs.write("reading stems done\n")
    logs.write("stemming from dict\n")
    logs.flush()
    logs.write("There is %d tweets\n"%len(prepResults.tweets))
    for t in prepResults.tweets:
        try:
            if t.isValid == True:
                logs.write("stemming tweet %s\n"%t.tweetId)
                stemmedData = t.get_stemmed(prepResults.words)
                logs.write("stemmed tweet resulted in %d words"%len(stemmedData))
                results.append(StemmingResult(t.tweetId, stemmedData))
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print message
            logs.write(message)
            logs.write('\n')
    logs.write("all stemmed\n")
    logs.write("Storing stuff to %s\n" %pathToStemmedTweets)
    logs.flush()
    storeStemmedData(pathToStemmedTweets, results, logs)
    logs.write("returning from storing stemmed\n")
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

    #print( "Creating stemmer" )
    #lib = ctypes.cdll.LoadLibrary('/home/zby/projects/spdb/spatial_tweet_clustering/libstemmer_c/libstemmer.so')
    #createStemmer = lib.sb_stemmer_new
    #createStemmer.restype = ctypes.c_void_p
    #createStemmer.argtpyes = [ctypes.c_char_p, ctypes.c_char_p]
    #deleteStemmer = lib.sb_stemmer_delete
    #deleteStemmer.argtypes = [ctypes.c_void_p]
    #doStemming = lib.sb_stemmer_stem
    #doStemming.argtpyes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    #doStemming.restype = ctypes.c_char_p
    #stemmer_p = createStemmer("en", "UTF_8")
