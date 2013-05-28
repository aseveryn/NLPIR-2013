# coding=utf8
#
# Copyright (c) 2012, Frane Saric
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
#   * If this software or its derivative is used to produce an academic
# publication, you are required to cite this work by using the citation
# provided on "http://takelab.fer.hr/sts".
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import math
from nltk.corpus import wordnet
import nltk
from collections import Counter, defaultdict
import os
import sys
import re
import numpy
from numpy.linalg import norm
import logging
from corpus_utils import (load_data, get_lemmatized_words, is_word, 
                          get_locase_words, make_ngrams, fix_compounds)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

WORD_FREQUENCIES_FILE = 'word-frequencies.txt'
# WORD_FREQUENCIES_FILE = 'sts2012_2013_word_frequencies.txt'

class Sim:
    def __init__(self, words, vectors):        
        self.word_to_idx = {a: b for b, a in
                            enumerate(w.strip() for w in open(words))}
        logging.info("Loading lsi vector file: %s", vectors)                            
        self.mat = numpy.loadtxt(vectors)

    def bow_vec(self, b):
        vec = numpy.zeros(self.mat.shape[1])
        for k, v in b.iteritems():
            idx = self.word_to_idx.get(k, -1)
            if idx >= 0:
                vec += self.mat[idx] / (norm(self.mat[idx]) + 1e-8) * v
        return vec

    def calc(self, b1, b2):
        v1 = self.bow_vec(b1)
        v2 = self.bow_vec(b2)
        return abs(v1.dot(v2) / (norm(v1) + 1e-8) / (norm(v2) + 1e-8))

def load_wweight_table(path):
    lines = open(path).readlines()
    wweight = defaultdict(float)
    if not len(lines):
        return (wweight, 0.)
    totfreq = int(lines[0])
    for l in lines[1:]:
        w, freq = l.split()
        freq = float(freq)
        if freq < 10:
            continue
        wweight[w] = math.log(totfreq / freq)
    logging.info("Loaded word frequency weights [{}] from: {}".format(len(wweight), path))
    return wweight

wweight = load_wweight_table(WORD_FREQUENCIES_FILE)
minwweight = min(wweight.values())


def len_compress(l):
    return math.log(1. + l)

def dist_sim(sim, la, lb):
    wa = Counter(la)
    wb = Counter(lb)
    d1 = {x:1 for x in wa}
    d2 = {x:1 for x in wb}
    return sim.calc(d1, d2)

def weighted_dist_sim(sim, lca, lcb):
    wa = Counter(lca)
    wb = Counter(lcb)
    wa = {x: wweight[x] * wa[x] for x in wa}
    wb = {x: wweight[x] * wb[x] for x in wb}
    return sim.calc(wa, wb)

def weighted_word_match(lca, lcb):
    wa = Counter(lca)
    wb = Counter(lcb)
    wsuma = sum(wweight[w] * wa[w] for w in wa)
    wsumb = sum(wweight[w] * wb[w] for w in wb)
    wsum = 0.

    for w in wa:
        wd = min(wa[w], wb[w])
        wsum += wweight[w] * wd
    p = 0.
    r = 0.
    if wsuma > 0 and wsum > 0:
        p = wsum / wsuma
    if wsumb > 0 and wsum > 0:
        r = wsum / wsumb
    f1 = 2 * p * r / (p + r) if p + r > 0 else 0.
    return f1

wpathsimcache = {}
def wpathsim(a, b):
    if a > b:
        b, a = a, b
    p = (a, b)
    if p in wpathsimcache:
        return wpathsimcache[p]
    if a == b:
        wpathsimcache[p] = 1.
        return 1.
    sa = wordnet.synsets(a)
    sb = wordnet.synsets(b)
    mx = max([wa.path_similarity(wb)
              for wa in sa
              for wb in sb
              ] + [0.])
    wpathsimcache[p] = mx
    return mx

def calc_wn_prec(lema, lemb):
    rez = 0.
    for a in lema:
        ms = 0.
        for b in lemb:
            ms = max(ms, wpathsim(a, b))
        rez += ms
    return rez / len(lema)

def wn_sim_match(lema, lemb):
    f1 = 1.
    p = 0.
    r = 0.
    if len(lema) > 0 and len(lemb) > 0:
        p = calc_wn_prec(lema, lemb)
        r = calc_wn_prec(lemb, lema)
        f1 = 2. * p * r / (p + r) if p + r > 0 else 0.
    return f1

def ngram_match(sa, sb, n):
    nga = make_ngrams(sa, n)
    ngb = make_ngrams(sb, n)
    matches = 0
    c1 = Counter(nga)
    for ng in ngb:
        if c1[ng] > 0:
            c1[ng] -= 1
            matches += 1
    p = 0.
    r = 0.
    f1 = 1.
    if len(nga) > 0 and len(ngb) > 0:
        p = matches / float(len(nga))
        r = matches / float(len(ngb))
        f1 = 2 * p * r / (p + r) if p + r > 0 else 0.
    return f1

def is_stock_tick(w):
    return w[0] == '.' and len(w) > 1 and w[1:].isupper()

def stocks_matches(sa, sb):
    ca = set(x[0] for x in sa if is_stock_tick(x[0]))
    cb = set(x[0] for x in sb if is_stock_tick(x[0]))
    isect = len(ca.intersection(cb))
    la = len(ca)
    lb = len(cb)

    f = 1.
    if la > 0 and lb > 0:
        if isect > 0:
            p = float(isect) / la
            r = float(isect) / lb
            f = 2 * p * r / (p + r)
        else:
            f = 0.
    return (len_compress(la + lb), f)

def case_matches(sa, sb):
    ca = set(x[0] for x in sa[1:] if x[0][0].isupper()
            and x[0][-1] != '.')
    cb = set(x[0] for x in sb[1:] if x[0][0].isupper()
            and x[0][-1] != '.')
    la = len(ca)
    lb = len(cb)
    isect = len(ca.intersection(cb))

    f = 1.
    if la > 0 and lb > 0:
        if isect > 0:
            p = float(isect) / la
            r = float(isect) / lb
            f = 2 * p * r / (p + r)
        else:
            f = 0.
    return (len_compress(la + lb), f)

risnum = re.compile(r'^[0-9,./-]+$')
rhasdigit = re.compile(r'[0-9]')

def match_number(xa, xb):
    if xa == xb:
        return True
    xa = xa.replace(',', '')
    xb = xb.replace(',', '')

    try:
        va = int(float(xa))
        vb = int(float(xb))
        if (va == 0 or vb == 0) and va != vb:
            return False
        fxa = float(xa)
        fxb = float(xb)
        if abs(fxa - fxb) > 1:
            return False
        diga = xa.find('.')
        digb = xb.find('.')
        diga = 0 if diga == -1 else len(xa) - diga - 1
        digb = 0 if digb == -1 else len(xb) - digb - 1
        if diga > 0 and digb > 0 and va != vb:
            return False
        dmin = min(diga, digb)
        if dmin == 0:
            if abs(round(fxa, 0) - round(fxb, 0)) < 1e-5:
                return True
            return va == vb
        return abs(round(fxa, dmin) - round(fxb, dmin)) < 1e-5
    except:
        pass

    return False

def number_features(sa, sb):
    numa = set(x[0] for x in sa if risnum.match(x[0]) and
            rhasdigit.match(x[0]))
    numb = set(x[0] for x in sb if risnum.match(x[0]) and
            rhasdigit.match(x[0]))
    isect = 0
    for na in numa:
        if na in numb:
            isect += 1
            continue
        for nb in numb:
            if match_number(na, nb):
                isect += 1
                break

    la, lb = len(numa), len(numb)

    f = 1.
    subset = 0.
    if la + lb > 0:
        if isect == la or isect == lb:
            subset = 1.
        if isect > 0:
            p = float(isect) / la
            r = float(isect) / lb
            f = 2. * p * r / (p + r)
        else:
            f = 0.
    return (len_compress(la + lb), f, subset)

def relative_len_difference(lca, lcb):
    la, lb = len(lca), len(lcb)
    return abs(la - lb) / float(max(la, lb) + 1e-5)

def relative_ic_difference(lca, lcb):
    #wa = sum(wweight[x] for x in lca)
    #wb = sum(wweight[x] for x in lcb)
    wa = sum(max(0., wweight[x] - minwweight) for x in lca)
    wb = sum(max(0., wweight[x] - minwweight) for x in lcb)
    return abs(wa - wb) / (max(wa, wb) + 1e-5)
