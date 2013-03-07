#! /bin/bash

indexDir=$1
maxHits=$2

java -cp bin:lib/* it.unitn.nlpir.lab01.QAInteractive $indexDir $maxHits