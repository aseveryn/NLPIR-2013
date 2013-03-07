#! /bin/bash

indexDir=$1
input=$2

java -cp bin:lib/* it.unitn.nlpir.lab01.QAIndex $indexDir $input