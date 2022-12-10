import json

from kafka import KafkaConsumer
from pymongo import MongoClient

CONNECTION_STRING = "mongodb://localhost/"

'''

The sentiment consumer listens for messages on the sentiment_output queue and processes them into a MongoDB. These
messages originate from the Flink stream processor and contain sentiment analysis of tweets. 

Ref: https://www.w3schools.com/python/python_mongodb_insert.asp
Ref: https://www.mongodb.com/languages/python

'''


def get_database():
    # Create a connection.
    client = MongoClient(CONNECTION_STRING)
    return client['sentiment']


def store_sentiment():
    db = get_database()
    collection = db['twitter']
    var = 1
    while var == 1:
        consumer = KafkaConsumer(bootstrap_servers='localhost:9092', group_id='consumer-1', auto_offset_reset='latest')
        consumer.subscribe(['sentiment_output'])
        for message in consumer:
            data = json.loads(message.value.decode("utf-8").replace("'", '"'))
            data_dict = json.loads(data['tweet'])
            print(data_dict)
            collection.insert_one(data_dict)


if __name__ == "__main__":
    # Read from the sentiment_output kafka queue
    store_sentiment()
