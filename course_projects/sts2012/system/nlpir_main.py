from __future__ import division
import logging
from takelab_simple_features import *
from corpus_utils import (load_data, get_locase_words, get_lemmatized_words, stopwords)
from sts_data import (get_sts_input_path,
                      FEATURE_PATH, TRAIN_SETS, TEST_SETS, TRAIN, TEST)
from util import make_dirs

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

FEATURE_SET = 'unitn.nlpir.word-match'


def word_similarity_match(sa, sb):
    ### YOUR CODE GOES HERE
    s1 = set(sa)
    s2 = set(sb)
    overlap = len(s1.intersection(s2))
    score = 0.0
    if not overlap == 0:
        score = 2.0/(len(sa)/overlap + len(sb)/overlap)
    return score


def compute_features(sa, sb):
    # lowcase
    olca = get_locase_words(sa)
    olcb = get_locase_words(sb)
    
    # lowcase with stopwords removed
    lca = [w for w in olca if w not in stopwords]
    lcb = [w for w in olcb if w not in stopwords]
    
    # lemmas
    lema = get_lemmatized_words(sa)
    lemb = get_lemmatized_words(sb)

    f = [
        word_similarity_match(lca, lcb),
        word_similarity_match(lema, lemb),
        ]

    return f


def extract_features(mode, datasets):
    for dataset in datasets:
        input = get_sts_input_path(mode, dataset)
        print dataset
        # print "Generating test files..."
        sentence_pairs = load_data(input)

        logging.info("Computing features")
        doc2features = []
        for i, sp in enumerate(sentence_pairs, 1):
            if i % 10 == 0:
                sys.stdout.write("%d.." % i)
            features = compute_features(*sp)
            doc2features.append(features)
        sys.stdout.write("%d\n" % i)
        
        outdir = os.path.join(FEATURE_PATH, mode, dataset, FEATURE_SET)
        make_dirs(outdir)
        logging.info("Writing features to: %s" % outdir)

        for idx in xrange(len(features)):
            outfile = os.path.join(outdir, "%s.txt" % idx)
            with open(outfile, 'w') as out:
                for doc_features in doc2features:
                    out.write("%f\n" % doc_features[idx])


if __name__ == "__main__":
    extract_features(TRAIN, TRAIN_SETS)
    extract_features(TEST, TEST_SETS)
    
