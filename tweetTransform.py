from rpy2.robjects.packages import importr, data
import numpy

import simplejson
import json
import os
import sys

class TweetsPlace:
    """ Place related to the tweet. It doesn't have to be a place of tweet origin.
    The tweet may simply refer to some place.
    """
    bounding_box = {
        'coordinates':[[]], # list of lists of 2-elements list of coordinates like: [[ [0,1], [1,1],[2,2] ]]
        'type': ''
        }
    country = '' #country full name
    full_name = '' # city and state
    name = '' #city
    place_type = '' # e.g. city
    def __init__(self):
        self.initialized = True

class TweetForClustering:
    """This class is meant to represent essential tweet data
    needed for clustering algorithms.
    """
    coords = [] # geoJSON longitude first, then latitude
    entities = { 
        'hashtags':[],
        'urls':[],
        'user_mentiones':[]
        } #not sure if we gonna use that
    id = sys.maxint #id as integer
    lang = '' # language code
    text = '' #utf-8 text
    def __init__(self):
        self.initialized = True
        
def object_decoder(obj):
    tweet = TweetForClustering()
    tweet.geo = obj['geo']
    return tweet

def stemData():
    print( "TODO stem data in all files" )
    pathStr = 'tweets/'
    for root, dirs, files in os.walk(pathStr, topdown=False):
        for file in files:
            f = open(file, 'r')
            allLines = ''
            for line in f:
                allLines = '{0}{1}'.format(allLines,line)
            
    return 


def makeMatrixFiles():
    print( "TODO generate files being a matrix representation (matrixEntries: each row is a tweet, each column is a feature, featureListing: each row is a word-feature mapping to column features in matrixEntries) of all files" )
    return 
