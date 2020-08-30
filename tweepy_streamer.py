from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import twitter_credential
import pandas as pd
import numpy as np


###     TWITTER CLIENNT
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client
    
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
  
    def get_friend_list(self, num_friends):
        friends = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friends.append(friend)
        return friends
    
    def get_home_timeline_tweets(self, num_tweets):
        home_tweets = []
        for home_tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_tweets.append(home_tweet)
        return home_tweets
    

###     TWITTER AUTHENTICATOR
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credential.API_KEY, twitter_credential.API_SECRET_KEY)
        auth.set_access_token(twitter_credential.ACCESS_TOKEN, twitter_credential.ACCESS_TOKEN_SECRET)
        return auth

class TwitterStreamer():
    """
    Class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tags_list):
        #This handles twitter authentication and the connection to the Twitter Streaming API 
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tags_list)



class TwitterListener(StreamListener):
    """
        This is a basic listener class that just prints received tweets to stdout overtime.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s"%str(e))
        return True
    
    def on_error(self, status):
        if status == 420:
            ###Retuning false on_data method in case rate limit occurs
            return False
        print(status)

class TweetAnalyzer():
    '''
    Functionality for analyzing and categorization tweet content
    '''
    def tweets_to_df(self, tweets):
        df = pd.DataFrame(data=[tweet.id for tweet in tweets], columns=['Id'])

        df['Tweets'] = np.array([tweet.text for tweet in tweets])
        df['Length'] = np.array([len(tweet.text) for tweet in tweets])
        df['Date'] = np.array([tweet.created_at for tweet in tweets])
        df['Source'] = np.array([tweet.source for tweet in tweets])
        df['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['Retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        
        return df


if __name__=="__main__":
    '''
    hash_tags_list = []
    fetched_tweets_filename = "tweets.json"
    twitter_client = TwitterClient('narendramodi')
    print(twitter_client.get_user_timeline_tweets(5))
    print("***************************************")
    print("**********                 ************")
    print(twitter_client.get_friend_list(5))
    print("***************************************")
    print("**********                 ************")
    print(twitter_client.get_home_timeline_tweets(5))
    '''

    #for analyzing tweets
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="Swamy39", count=20)
    
    df = tweet_analyzer.tweets_to_df(tweets)
    print(df)

    #twitter_streamer = TwitterStreamer()
    #twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tags_list)
    