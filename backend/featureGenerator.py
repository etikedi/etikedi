import collections
import math

import nltk
from nltk.corpus import stopwords
from flask_sqlalchemy import SQLAlchemy
from models.resumees import Resumees
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
''' 
s1: convert cv into tokens
s2: features per token
s3: classify tokens

feature ideas:

    * unicode dot in front of word? (-> list!)
    * title of last headline
    * empty line before?

POS -> skills sind genau NICHT pos getagged
 kommas zwischen wörtern, etc.
'''
app = Flask(__name__)
app.config.from_object('config.Config')

with app.app_context():
    db.init_app(app)
    corpus = []

    for resumee in Resumees.query.limit(1).all():
        corpus.append(resumee.content)

    corpus_text = "".join([c for c in corpus])

    tokens = nltk.word_tokenize(corpus_text)

    # Tokenizing lower-case article into alphanumeric words [no punctuation]
    lower_alpha_tokens = [w for w in tokens if w.isalpha()]

    no_stop_tokens = [
        t for t in lower_alpha_tokens if t not in stopwords.words('english')
    ]

    counter_var = collections.Counter(no_stop_tokens)

    # pos tuples
    tagged = nltk.pos_tag(no_stop_tokens)

    # pos tree
    entities = nltk.chunk.ne_chunk(tagged)

    print(tagged)

    # output: [(token, [feature1, feature2, feature3]), (token, [feature1, feature2, feature 3])]
