import os

# File format for STS input files
STS_PATH = "."
DATASETS_PATH = os.path.join(STS_PATH, "datasets")

STS_FILE_FORMAT = "STS.input.%s.txt"
STS_GS_FILE_FORMAT = "STS.gs.%s.txt"

# Path to the golden labels
GOLD_PATH = os.path.join(DATASETS_PATH, "gold")

TRAIN = "train"
TEST = "test"
TRAIN_SETS = ["MSRpar", "MSRvid", "SMTeuroparl"]
TEST_SETS = ["MSRpar", "MSRvid", "SMTeuroparl", "OnWN",  "SMTnews"]

# Path to the generated features
FEATURE_PATH = os.path.join(STS_PATH, "features")
FEATURE_SET = "takelab"

def get_sts_gs_path(mode, dataset):
  return os.path.join(GOLD_PATH, mode, STS_GS_FILE_FORMAT % dataset)

def get_sts_input_path(mode, dataset):
  input_dir = os.path.join(DATASETS_PATH, mode)
  input_file = STS_FILE_FORMAT % dataset
  input_path = os.path.join(input_dir, input_file)
  return input_path

def get_sts_feature_path(mode, dataset, feature_set):
  return os.path.join(FEATURE_PATH, mode, dataset, feature_set)