import tweepy
from conf import *

MAX_CHARS = 140

auth_handler = None
api = None


def auth():
    global auth_handler, api
    auth_handler = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth_handler.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth_handler)


def send(tweet):
    api.update_status(status=tweet)

if __name__ == '__main__':
    auth()
