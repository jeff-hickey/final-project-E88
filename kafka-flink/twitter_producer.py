import time
from json import dumps

import tweepy
from kafka import KafkaProducer
from langdetect import detect

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIuEkAEAAAAAJ%2BtFew1tGw2RXPQxMFT4mVo46%2Fg%3D7OTwF0GcJE6icDPPZtRjgodK0PHUUYmfirrSo8T09svCtSDJIz"

producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: dumps(x).encode('utf-8'))

'''

The twitter producer builds a connection to the Twitter data stream using the tweepy StreamingClient. The stream 
samples 5% of the total twitter data on the stream. These tweets are sent as json documens to the kafka 
sentiment_input topic for stream processing by Flink. 

Ref: https://docs.tweepy.org/en/stable/streaming.html
Ref: https://pypi.org/project/langdetect/ 

'''


class TweetPrinter(tweepy.StreamingClient):

    def on_tweet(self, tweet):
        if tweet.text:
            try:
                lang = detect(tweet.text)
                if lang and lang == 'en':
                    # Send the tweet to kafka for processing.
                    data = {'tweet': f'{tweet.text}'}
                    producer.send('sentiment_input', data)
                    time.sleep(5)
                    print(lang, '-', tweet.id, '-', tweet)
            except Exception as err:
                print(err)


# Create a client to the Twitter stream.
printer = TweetPrinter(BEARER_TOKEN)
# samples 5% of all tweets.
printer.sample()

'''
for e in range(1000):
    data = {'tweet': 'Hello World'}
    producer.send('sentiment_input', value=data)
    time.sleep(5)
'''
