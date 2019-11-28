import collections
import math

import nltk
from nltk.corpus import stopwords
from models import db
from models.resumee import Resumee
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

#  corpus = []

for resumee in Resumee.query.limit(100).all():
    #  corpus.append(resumee.content)

    #  corpus_text = "".join([c for c in corpus])
    corpus_text = resumee.content

    tokens = nltk.word_tokenize(corpus_text)

    # Tokenizing lower-case article into alphanumeric words [no punctuation]
    lower_alpha_tokens = [w for w in tokens if w.isalpha()]

    no_stop_tokens = [
        t for t in lower_alpha_tokens if t not in stopwords.words('english')
    ]

    counter_var = collections.Counter(no_stop_tokens)

    print(counter_var.most_common(300))

    tagged = nltk.pos_tag(no_stop_tokens)
    #  print(tagged)

    entities = nltk.chunk.ne_chunk(tagged)
    print(entities)
    print("\n" * 10)
