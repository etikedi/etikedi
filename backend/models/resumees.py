import collections
import re
from datetime import datetime
from pprint import pprint
from spellchecker import SpellChecker
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

    #  label = db.Column(db.Integer, default=0)

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

        # create current_line -> tokens

        lines = {0: ""}
        tokens_context = []

        current_line_index = 0
        for tagging in tagged:
            token = tagging[0]
            tokens_context.append((token, tagging[1], current_line_index))
            if "\n" not in token:
                lines[current_line_index] += token
            else:
                current_line_index += 1
                lines[current_line_index] = ""

        speller = SpellChecker()

        for tagging in tokens_context:
            token = tagging[0]
            line = lines[tagging[2]]
            feature = {}
            feature['pos'] = tagging[1]

            feature['term_length'] = len(token)

            # if beginning charachter is not in ascii we guess that it is a bullet list
            feature['is_begginning_of_line_non_ascii'] = False if 0 <= ord(
                line[0]) <= 127 else True

            feature['is_beginning_of_line_number'] = True if '0' <= line[
                0] <= '9' else False

            feature['amount_of_commas_in_line'] = sum(c == ',' for c in line)

            feature['amount_of_uppercase_letters_in_term'] = sum(
                c.isupper() for c in token)
            feature['amount_of_digits_in_term'] = sum(c.isdigit()
                                                      for c in token)
            #  feature['count_spell_corrections'] = len(
            #  speller.candidates(word=token))

            #TODOS:
            # save features in ?
            # select text by selecting it -> click button label as X -> save labels for selected tokens -> display selected labels

            feature['label'] = 'unspecified'

            # convert line breaks to html
            if "\n" in tagging[0]:
                tagging = ("<br>" * tagging[0].count("\n"), feature)
            features.append((tagging[0], feature))

        return features

    def as_dict(self):
        result = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
        result['features'] = self.generateFeatures()
        return result


class ResumeesApi(Resource):
    def get(self, resumeeId):
        result = Resumees.query.get(resumeeId).as_dict()
        pprint(result)
        return result


class ResumeesListApi(Resource):
    def get(self):
        resumees = []
        for r in Resumees.query.all():
            resumees.append(r.as_dict())
        return resumees
