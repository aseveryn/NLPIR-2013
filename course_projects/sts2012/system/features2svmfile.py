import os
import sys
import random
import math
import logging
import re
from collections import defaultdict
from util import make_dirs
from sts_data import get_sts_input_path, get_sts_gs_path
from corpus_utils import Alphabet

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

SVMTK_TREE_PAT = re.compile(r"\s*\|[BE]T\|\s*")

TRAIN_ALL = "ALL"
TRAIN = "train"
TEST = "test"
TRAIN_SETS = [
  "MSRpar", 
  "MSRvid", 
  "SMTeuroparl",
  ]
TEST_SETS = ["MSRpar", "MSRvid", "SMTeuroparl", "OnWN",  "SMTnews"]

# SVM_FORMAT="svmtk"
SVM_FORMAT="libsvm"

# Path to the generated features
FEATURE_PATH = "features"

# Names of the folders containing features
FEATURES = [
  # "n-grams", 
  # "string", 
  "takelab.simple", 
  ]

CORPUS_TYPES = ["MSRpar", "MSRvid", "SMTeuroparl", "OnWN",  "SMTnews"]

TREE_TYPE = "constituency"

# Name of the output model
MODEL = ".".join(FEATURES)
if SVM_FORMAT == "svmtk":
  MODEL = TREE_TYPE + "." + MODEL

MODEL_PATH = "models"


def get_gold_labels(mode, dataset):
  fname = get_sts_gs_path(mode, dataset)
  if os.path.exists(fname):
    gs = {}
    with open(fname) as input:    
      for i, line in enumerate(input):
        gs[i] = line.strip()
  else:
    logging.warn("No gold targets found for {} [{}]. Filling with dummy values.".format(dataset, mode))
    gs = dict((i, 0.0) for i, _ in enumerate(open(get_sts_input_path(mode, dataset))))
  return gs


alphabet = Alphabet()

def combine_features(mode, dataset, features):
  doc2features = defaultdict(dict)
  for fset in features:
    p = os.path.join(FEATURE_PATH, mode, dataset, fset)
    for feature_file in os.listdir(p):
      fname = os.path.join(p, feature_file)
      with open(fname) as input:
        for i, line in enumerate(input):
          fval = float(line.strip())
          if math.isnan(fval):
            continue
          fid = alphabet.add(feature_file)
          doc2features[i][fid] = fval
  return doc2features


def get_tree(mode, dataset, tree_type):
  fname = os.path.join(FEATURE_PATH, mode, 
                       dataset, "trees", 
                       tree_type + ".txt")
  trees = {}
  with open(fname) as input:
    for i, line in enumerate(input):
      trees[i] = line.strip()
  return trees

class ExampleWriter:
  def __init__(self, format):
    self.format = format

  def to_svm(self, mode, dataset):
    foo = getattr(self, "to_%s" % self.format)
    return foo(mode, dataset)

  def to_svmtk(self, mode, dataset):
    if not TREE_TYPE:
      sys.stderr.write("Tree type is not specified")  
      sys.exit(1)
    trees = get_tree(mode, dataset, TREE_TYPE)
    features = combine_features(mode, dataset, FEATURES)
    gs = get_gold_labels(mode, dataset)
    for key, features in features.iteritems():
      label = gs[key]
      tree = trees[key]
      fvec = ["%d:%s" % (i, feat) for i, feat in sorted(features.items())]
      fvec = " ".join(fvec)
      example = "%s %s %s |EV|\n" % (label, tree, fvec)
      yield example


  def to_libsvm(self, mode, dataset):  
    features = combine_features(mode, dataset, FEATURES)
    gs = get_gold_labels(mode, dataset)
    for key, features in features.iteritems():
      label = gs[key]
      fvec = ["%d:%s" % (i, feat) for i, feat in sorted(features.items())]
      fvec = " ".join(fvec)
      example = "%s %s\n" % (label, fvec)
      yield example


def write_svmfile(mode, datasets):
  print "Generating files in %s mode..." % mode
  
  examples = []
  outdir = os.path.join(MODEL_PATH, MODEL, mode)
  make_dirs(outdir)
  for dataset in datasets:
    outfile = "%s.svmtk" % dataset
    outpath = os.path.join(outdir, outfile)
    print outpath
    with open(outpath, "w") as out:
      ex_generator = ExampleWriter(SVM_FORMAT)
      for ex in ex_generator.to_svm(mode, dataset):
        out.write(ex)
        examples.append(ex)

  # if mode == TRAIN:
  random.seed(123)
  random.shuffle(examples)

  outfile = "ALL.svmtk"
  outpath = os.path.join(outdir, outfile)
  print outpath
  with open(outpath, "w") as out:
    for ex in examples:
      out.write(ex)


def main():
  write_svmfile(TRAIN, TRAIN_SETS)
  write_svmfile(TEST, TEST_SETS)
    

if __name__ == '__main__':
  main()

