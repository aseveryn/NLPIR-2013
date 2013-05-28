import os
import shutil

def make_dirs(path):
  if os.path.exists(path):
    shutil.rmtree(path)
  os.makedirs(path)