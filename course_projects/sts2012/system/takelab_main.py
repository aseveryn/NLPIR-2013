import logging
from takelab_simple_features import *
from corpus_utils import (load_data, get_locase_words, get_lemmatized_words, stopwords)
from sts_data import (get_sts_input_path,
                      FEATURE_PATH, TRAIN_SETS, TEST_SETS, TRAIN, TEST)
from util import make_dirs

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

FEATURE_SET = 'takelab.simple'

def compute_features(sa, sb):
    olca = get_locase_words(sa)
    olcb = get_locase_words(sb)
    lca = [w for w in olca if w not in stopwords]
    lcb = [w for w in olcb if w not in stopwords]
    lema = get_lemmatized_words(sa)
    lemb = get_lemmatized_words(sb)

    f = []
    f += number_features(sa, sb)
    f += case_matches(sa, sb)
    f += stocks_matches(sa, sb)
    f += [
            ngram_match(lca, lcb, 1),
            ngram_match(lca, lcb, 2),
            ngram_match(lca, lcb, 3),
            ngram_match(lema, lemb, 1),
            ngram_match(lema, lemb, 2),
            ngram_match(lema, lemb, 3),
            wn_sim_match(lema, lemb),
            weighted_word_match(olca, olcb),
            weighted_word_match(lema, lemb),

            # dist_sim(nyt_sim, lema, lemb),
            #dist_sim(wiki_sim, lema, lemb),
            # weighted_dist_sim(nyt_sim, lema, lemb),
            # weighted_dist_sim(wiki_sim, lema, lemb),

            relative_len_difference(lca, lcb),
            relative_ic_difference(olca, olcb)
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
    
