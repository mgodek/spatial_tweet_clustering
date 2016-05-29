from __future__ import absolute_import, print_function
from __future__ import division

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import simplejson
import json
import os
import sys

class AccessTokens:
    # Go to http://apps.twitter.com and create an app.
    # The consumer key and secret will be generated for you after
    consumer_key=""#read json file, which will not be added to git
    consumer_secret=""
    # The access tokens can be found on your applications's Details
    # page located at https://dev.twitter.com/apps (located
    # under "Your access token")
    access_token=""
    access_token_secret=""
    
    def __init__(self, tokenFileName):
        self.consumer_key=""
        self.consumer_secret=""
        self.access_token=""
        self.access_token_secret=""
        #save to json
        #jsondata = simplejson.dumps(aTok.__dict__, indent=4, skipkeys=True, sort_keys=True)
        #fd = open("applicationTokens.json", 'w')
        #fd.write(jsondata)
        #fd.close()
        
        #read from json
        with open(tokenFileName) as json_file:
            json_data = json.load(json_file)
            #print(json_data)
            self.consumer_key=json_data["consumer_key"]
            self.consumer_secret=json_data["consumer_secret"]
            self.access_token=json_data["access_token"]
            self.access_token_secret=json_data["access_token_secret"]
            print(self.__dict__)

class StdOutListener(StreamListener):

    def __init__(self):
        super(StdOutListener, self).__init__()
        self.num_tweets = 0
	self.amount = maxAmount

    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
	#use https://git-lfs.github.com/ to store collected data
    	#gather tweets and save them to file
        jsonData = json.loads(data);
        #print(jsonData)
        directory="tweets"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        #if not jsonData["id_str"]:
        if 'id_str' in data:
            with open(directory+"/"+jsonData["id_str"]+".json", 'w') as outfile:
                json.dump(jsonData, outfile)
                outfile.close()

        self.num_tweets += 1
        if self.num_tweets > self.amount:
            print( "" )
            return False

	progress = (self.num_tweets / self.amount)*100
	sys.stdout.write("\r%d%%" % progress)
        sys.stdout.flush()
	return True

    def on_error(self, status):
        print(status)

def fetchTweets(amount):
    global maxAmount
    maxAmount = amount
    
    l = StdOutListener()
    aTok = AccessTokens("applicationTokens.json")
    auth = OAuthHandler(aTok.consumer_key, aTok.consumer_secret)
    auth.set_access_token(aTok.access_token, aTok.access_token_secret)
    stream = Stream(auth, l)
    EUROPE_BB=[-31.266001, 27.636311, 39.869301, 81.008797]
    WORLD_BB=[-180.0,-90.0,180.0,90.0]
    stream.filter(languages=["en"], locations=EUROPE_BB)
