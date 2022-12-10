from flask import Flask
from flask import render_template
from pymongo import MongoClient

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

CONNECTION_STRING = "mongodb://localhost/"

'''
Reference: https://realpython.com/python-nltk-sentiment-analysis/
'''


def get_database():
    # Create a connection.
    client = MongoClient(CONNECTION_STRING)
    return client['sentiment']


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


@app.route("/")
def hello_world():
    cursor = summarize_sentiment()
    summary = None
    pos, neu, neg, comp = 0, 0, 0, 0
    if cursor:
        summary = [doc for doc in cursor]

    if summary is not None and len(summary) > 0:
        summary = summary[0]
        pos = round(summary.get('pos_avg') * 100, 1)
        neu = round(summary.get('neu_avg') * 100, 1)
        neg = round(summary.get('neg_avg') * 100, 1)
        comp = round(summary.get('comp_avg') * 100, 1)
    return render_template('index.html',
                           positive=pos,
                           neutral=neu,
                           negative=neg,
                           current=max([pos, neu, neg]),
                           compound=comp)
