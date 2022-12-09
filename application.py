from datetime import datetime

from flask import render_template
from pymongo import MongoClient
from nltk.sentiment import SentimentIntensityAnalyzer
from random import shuffle
from flask import Flask
import nltk

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

CONNECTION_STRING = "mongodb://localhost/"

'''
Reference: https://realpython.com/python-nltk-sentiment-analysis/
'''


# db.twitter.find({ "created_on": { "$gte": ISODate("2022-12-07T00:00:00.000Z") } })
# db.twitter.aggregate([{ $group: { "_id": "_id", neg_avg: { $avg:"$neg" }, neu_avg: {$avg: "$neu"}, pos_avg: "$pos" } }])


def summarize_sentiment():
    db = get_database()
    collection = db['twitter']
    return collection.aggregate([{'$group':
        {
            '_id': '_id', 'neg_avg': {'$avg': '$neg'},
            'neu_avg': {'$avg': '$neu'}, 'pos_avg': {'$avg': '$pos'},
            'comp_avg': {'$avg': '$compound'}
        }
    }])


def analyze_sentiment(text):
    # {'neg': 0.0, 'neu': 0.295, 'pos': 0.705, 'compound': 0.8012}
    sia = SentimentIntensityAnalyzer()
    sia.polarity_scores(text)


def create_word_list(text):
    text = """
    ... For some quick analysis, creating a corpus could be overkill.
    ... If all you need is a word list,
    ... there are simpler ways to achieve that goal."""
    return nltk.word_tokenize(text)


@app.route("/")
def hello_world():
    # nltk.download('vader_lexicon', 'twitter_samples')
    cursor = summarize_sentiment()
    if cursor:
        summary = [doc for doc in cursor][0]
    pos = round(summary.get('pos_avg') * 100, 1)
    neu = round(summary.get('neu_avg') * 100, 1)
    neg = round(summary.get('neg_avg') * 100, 1)

    '''
    db = get_database()
    collection = db['twitter']
    tweets = [t.replace("://", "//") for t in nltk.corpus.twitter_samples.strings()]
    shuffle(tweets)
    sia = SentimentIntensityAnalyzer()
    for tweet in tweets[:10]:
        sentiment = sia.polarity_scores(tweet)
        sentiment['created_on'] = datetime.now()
        result = collection.insert_one(sentiment)
        print(result)
        print(">", is_positive(tweet), tweet)
    '''
    return render_template('index.html',
                           positive=pos,
                           neutral=neu,
                           negative=neg,
                           current=max([pos, neu, neg]),
                           compound=round(summary.get('comp_avg') * 100, 1))


def is_positive(tweet: str) -> bool:
    """True if tweet has positive compound sentiment, False otherwise."""
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(tweet)["compound"] > 0


def get_database():
    # Create a connection.
    client = MongoClient(CONNECTION_STRING)
    return client['sentiment']


'''
tweets = [t.replace("://", "//") for t in nltk.corpus.twitter_samples.strings()]
shuffle(tweets)
sia = SentimentIntensityAnalyzer()
for tweet in tweets[:10]:
    sentiment = sia.polarity_scores(tweet)
    sentiment['created_on'] = datetime.now()
    result = collection.insert_one(sentiment)
    print(result)
    print(">", is_positive(tweet), tweet)
'''
