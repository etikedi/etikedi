import collections
import re
from datetime import datetime

import nltk
import sqlalchemy
from flask_restful import Resource, reqparse
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from sqlalchemy.orm import class_mapper

from models import db


class Resumees(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), unique=False, nullable=False)
    label = db.Column(db.Integer)

    def generateFeatures(self):

        #  tokens = nltk.word_tokenize(self.content)
        tokens = RegexpTokenizer(r'(\s+)', gaps=True).tokenize(self.content)
        # Tokenizing lower-case article into alphanumeric words [no punctuation]
        #  lower_alpha_tokens = [w for w in tokens if w.isalpha()]

        #  no_stop_tokens = [
        #  t for t in lower_alpha_tokens
        #  if t not in stopwords.words('english')
        #  ]

        #  counter_var = collections.Counter(no_stop_tokens)

        # pos tuples
        tagged = nltk.pos_tag(tokens)

        # pos tree
        #  entities = nltk.chunk.ne_chunk(tagged)

        features = []

        for tagging in tagged:
            feature = {}
            feature['pos'] = tagging[1]
            feature['length'] = len(tagging[0])
            if "\n" in tagging[0]:
                tagging = ("<br>" * tagging[0].count("\n"), feature)
            features.append((tagging[0], feature))

        return features

        # output: [(token, [feature1, feature2, feature3]), (token, [feature1, feature2, feature 3])]

    def as_dict(self):
        result = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
        result['features'] = self.generateFeatures()
        return result


class ResumeesApi(Resource):
    def get(self, resumeeId):
        return Resumees.query.get(resumeeId).as_dict()


class ResumeesListApi(Resource):
    def get(self):
        resumees = []
        for r in Resumees.query.all():
            #  p
            #  resumee = _prepare_dict_for_json(r.__dict__)
            resumees.append(r.as_dict())
        return resumees
