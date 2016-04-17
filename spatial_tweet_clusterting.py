from __future__ import absolute_import, print_function

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import simplejson
import json

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
            print(json_data)
            self.consumer_key=json_data["consumer_key"]
            print(self.__dict__)

aTok = AccessTokens("applicationTokens.json")


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(aTok.consumer_key, aTok.consumer_secret)
    auth.set_access_token(aTok.access_token, aTok.access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['basketball'])

