# coding=utf8
#

import os
import re
import cPickle
import logging
import math
from nltk.corpus import wordnet

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

stopwords = set([
"i", "a", "about", "an", "are", "as", "at", "be", "by", "for", "from",
"how", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
"was", "what", "when", "where", "who", "will", "with", "the", "'s", "did",
"have", "has", "had", "were", "'ll", "but",
])


def normalize(fvec):
  # compute norm
  norm = 0.0
  for fval in fvec.itervalues():
    norm += fval*fval
  norm = math.sqrt(norm)
  # normalize each value
  for fid in fvec:
    fvec[fid] /= norm


class Alphabet:
  def __init__(self, start_feature_id=100):
    self.vocabulary = {}
    self.fid = start_feature_id

  def add(self, item):
    idx = self.vocabulary.get(item, None)
    if not idx:
      idx = self.fid
      self.vocabulary[item] = idx
      self.fid += 1
    return idx

  def __len__(self):
    return len(self.vocabulary)



def load_data(path):
    serialized_file = os.path.splitext(path)[0] + '.dat'
    if os.path.exists(serialized_file):
        logging.info("Serialized dataset found: %s" % serialized_file)
        return cPickle.load(open(serialized_file, 'rb'))
    
    logging.info("Preprocessing dataset: %s" % path)
    sentences_pos = []
    r1 = re.compile(r'\<([^ ]+)\>')
    r2 = re.compile(r'\$US(\d)')
    for idx, l in enumerate(open(path), 1):
        if idx % 10 == 0:
            sys.stdout.write("\r%8d" % idx)

        l = l.decode('utf-8')
        l = l.replace(u'’', "'")
        l = l.replace(u'``', '"')
        l = l.replace(u"''", '"')
        l = l.replace(u"—", '--')
        l = l.replace(u"–", '--')
        l = l.replace(u"´", "'")
        l = l.replace(u"-", " ")
        l = l.replace(u"/", " ")
        l = r1.sub(r'\1', l)
        l = r2.sub(r'$\1', l)
        s = l.strip().split('\t')
        sa, sb = tuple(nltk.word_tokenize(s)
                          for s in l.strip().split('\t'))
        sa, sb = ([x.encode('utf-8') for x in sa],
                  [x.encode('utf-8') for x in sb])

        for s in (sa, sb):
            for i in xrange(len(s)):
                if s[i] == "n't":
                    s[i] = "not"
                elif s[i] == "'m":
                    s[i] = "am"
        sa, sb = fix_compounds(sa, sb), fix_compounds(sb, sa)
        sentences_pos.append((nltk.pos_tag(sa), nltk.pos_tag(sb)))
    sys.stdout.write("\r%8d\n" % idx)

    logging.info("Serializing dataset: %s" % serialized_file)
    cPickle.dump(sentences_pos, open(serialized_file, 'wb'))
    return sentences_pos


def get_lemmatized_words(sa):
    rez = []
    for w, wpos in sa:
        w = w.lower()
        if w in stopwords or not is_word(w):
            continue
        wtag = to_wordnet_tag.get(wpos[:2])
        if wtag is None:
            wlem = w
        else:
            wlem = wordnet.morphy(w, wtag) or w
        rez.append(wlem)
    return rez

def len_compress(l):
    return math.log(1. + l)

to_wordnet_tag = {
        'NN':wordnet.NOUN,
        'JJ':wordnet.ADJ,
        'VB':wordnet.VERB,
        'RB':wordnet.ADV
    }

word_matcher = re.compile('[^0-9,.(=)\[\]/_`]+$')
def is_word(w):
    return word_matcher.match(w) is not None

def get_locase_words(spos):
    return [x[0].lower() for x in spos
            if is_word(x[0])]


def get_pos_tags(spos):
    return [x[1] for x in spos if is_word(x[0])]


def make_ngrams(l, n):
    rez = [l[i:(-n + i + 1)] for i in xrange(n - 1)]
    rez.append(l[n - 1:])
    return zip(*rez)

def fix_compounds(a, b):
    sb = set(x.lower() for x in b)

    a_fix = []
    la = len(a)
    i = 0
    while i < la:
        if i + 1 < la:
            comb = a[i] + a[i + 1]
            if comb.lower() in sb:
                a_fix.append(a[i] + a[i + 1])
                i += 2
                continue
        a_fix.append(a[i])
        i += 1
    return a_fix
